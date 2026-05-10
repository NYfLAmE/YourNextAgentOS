package paos

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

type LLMClient interface {
	DraftRuntimeTask(ctx context.Context, cfg LLMConfig, payload LLMPayload) (DraftResponse, error)
}

type OpenAICompatibleClient struct {
	HTTPClient *http.Client
}

func (c OpenAICompatibleClient) DraftRuntimeTask(ctx context.Context, cfg LLMConfig, payload LLMPayload) (DraftResponse, error) {
	if err := validateLLMConfig(Config{LLM: cfg}); err != nil {
		return DraftResponse{}, err
	}
	apiKey := os.Getenv(cfg.APIKeyEnv)
	body := map[string]any{
		"model": cfg.Model,
		"messages": []map[string]string{
			{
				"role":    "system",
				"content": "You draft Personal Agent OS Runtime Tasks. Return one JSON object only. Do not use Markdown fences. Do not execute commands, approve work, or infer missing required fields.",
			},
			{
				"role":    "user",
				"content": renderLLMPayload(payload),
			},
		},
		"response_format": map[string]string{"type": "json_object"},
	}
	reqBytes, err := json.Marshal(body)
	if err != nil {
		return DraftResponse{}, err
	}
	endpoint, err := chatCompletionsURL(cfg.BaseURL)
	if err != nil {
		return DraftResponse{}, err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(reqBytes))
	if err != nil {
		return DraftResponse{}, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	client := c.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: 60 * time.Second}
	}
	resp, err := client.Do(req)
	if err != nil {
		return DraftResponse{}, err
	}
	defer resp.Body.Close()
	respBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return DraftResponse{}, err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return DraftResponse{}, fmt.Errorf("llm provider returned %s: %s", resp.Status, strings.TrimSpace(string(respBytes)))
	}
	var parsed struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}
	if err := json.Unmarshal(respBytes, &parsed); err != nil {
		return DraftResponse{}, fmt.Errorf("parse provider response: %w", err)
	}
	if len(parsed.Choices) == 0 || strings.TrimSpace(parsed.Choices[0].Message.Content) == "" {
		return DraftResponse{}, fmt.Errorf("provider response has no message content")
	}
	return parseDraftResponse(parsed.Choices[0].Message.Content)
}

func chatCompletionsURL(base string) (string, error) {
	base = strings.TrimSpace(base)
	if base == "" {
		return "", fmt.Errorf("base_url is required")
	}
	u, err := url.Parse(base)
	if err != nil {
		return "", err
	}
	if u.Scheme == "" || u.Host == "" {
		return "", fmt.Errorf("base_url must be absolute")
	}
	path := strings.TrimRight(u.Path, "/")
	if strings.HasSuffix(path, "/chat/completions") {
		u.Path = path
	} else {
		u.Path = path + "/chat/completions"
	}
	return u.String(), nil
}

func parseDraftResponse(content string) (DraftResponse, error) {
	content = strings.TrimSpace(content)
	var draft DraftResponse
	dec := json.NewDecoder(strings.NewReader(content))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&draft); err != nil {
		return DraftResponse{}, fmt.Errorf("invalid structured draft response: %w", err)
	}
	var extra any
	if err := dec.Decode(&extra); err != io.EOF {
		return DraftResponse{}, fmt.Errorf("invalid structured draft response: trailing JSON values")
	}
	if err := validateDraftResponse(draft); err != nil {
		return DraftResponse{}, err
	}
	return draft, nil
}

func validateDraftResponse(draft DraftResponse) error {
	if strings.TrimSpace(draft.Title) == "" {
		return fmt.Errorf("draft.title is required")
	}
	if strings.TrimSpace(draft.Goal) == "" {
		return fmt.Errorf("draft.goal is required")
	}
	if err := validateExecutionSpec(draft.ExecutionSpec); err != nil {
		return fmt.Errorf("draft.execution_spec: %w", err)
	}
	return nil
}

func renderLLMPayload(payload LLMPayload) string {
	var b strings.Builder
	fmt.Fprintf(&b, "Mode: %s\n", payload.Mode)
	fmt.Fprintf(&b, "Parent path: %s\n", payload.ParentPath)
	fmt.Fprintf(&b, "Parent artifact type: %s\n", payload.ParentArtifact.Type)
	fmt.Fprintf(&b, "Parent status: %s\n", payload.ParentArtifact.Status)
	fmt.Fprintf(&b, "Parent approval_state: %s\n\n", payload.ParentArtifact.ApprovalState)
	b.WriteString("Required JSON schema:\n")
	b.WriteString(`{"title":"...","goal":"...","execution_spec":{"execution_workspace":{"repo":"...","mode":"dedicated_worktree","worktree_root":"private_runtime_config"},"command_list":[{"id":"...","command":"...","allowed_args":{},"repeatable":true}],"env_profile":{"mode":"empty","allow":[]},"network_intent":{"enabled":true,"reason":"..."},"private_runtime_log":{"storage":"private_runtime_directory","retention":"long_term","redaction":"none"}},"risks":[],"source_refs":[],"comments":[]}`)
	b.WriteString("\n\nParent Control Plane text:\n")
	b.WriteString(payload.ParentBody)
	if len(payload.ContextPack) > 0 {
		b.WriteString("\n\nContext pack from frontmatter source_refs:\n")
		for _, item := range payload.ContextPack {
			fmt.Fprintf(&b, "\n### %s\n", item.Path)
			fmt.Fprintf(&b, "status: %s\nsource: %s\nbytes: %d\ntruncated: %t\nreason: %s\n", item.Status, item.Source, item.Bytes, item.Truncated, item.Reason)
			if item.Status == "included" {
				b.WriteString("content:\n")
				b.WriteString(item.Content)
				if !strings.HasSuffix(item.Content, "\n") {
					b.WriteString("\n")
				}
			}
		}
	}
	b.WriteString("\n\nDomain context summary:\n")
	b.WriteString(payload.ContextSummary)
	b.WriteString("\n\nADR summaries:\n")
	for _, key := range sortedMapKeys(payload.ADRSummaries) {
		fmt.Fprintf(&b, "\n### %s\n%s\n", key, payload.ADRSummaries[key])
	}
	b.WriteString("\nRuntime Task template:\n")
	b.WriteString(payload.RuntimeTaskTmpl)
	if payload.Mode == "repair" {
		b.WriteString("\n\nFailed task result summary:\n")
		b.WriteString(payload.ResultSummary)
		b.WriteString("\n\nRuntime log references only, not log contents:\n")
		for _, ref := range payload.RuntimeLogRefs {
			fmt.Fprintf(&b, "- %s\n", ref)
		}
	}
	b.WriteString("\nExcluded data boundary:\n")
	for _, note := range payload.ExcludedDataNotes {
		fmt.Fprintf(&b, "- %s\n", note)
	}
	return b.String()
}
