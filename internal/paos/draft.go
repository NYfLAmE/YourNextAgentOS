package paos

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func BuildLLMPayload(root, parentPath string) (LLMPayload, error) {
	doc, err := ReadDocument(parentPath)
	if err != nil {
		return LLMPayload{}, err
	}
	artifact := Artifact{
		Path:           parentPath,
		RelPath:        repoRel(root, parentPath),
		Type:           fieldString(doc.Fields, "artifact_type"),
		Title:          fieldString(doc.Fields, "title"),
		Status:         fieldString(doc.Fields, "status"),
		ApprovalState:  fieldString(doc.Fields, "approval_state"),
		ParentRefs:     fieldStringSlice(doc.Fields, "parent_refs"),
		ApprovalRefs:   fieldStringSlice(doc.Fields, "approval_refs"),
		RuntimeLogRefs: fieldStringSlice(doc.Fields, "runtime_log_refs"),
	}
	mode := "parent"
	resultSummary := ""
	if artifact.Type == "runtime_task" && artifact.Status == "failed" {
		mode = "repair"
		resultSummary = extractSection(doc.Body, "Result")
	}
	contextSummary := readOptional(filepath.Join(root, "CONTEXT.md"), 8000)
	adrSummaries := map[string]string{}
	for _, name := range []string{
		"0005-strict-llm-output-contract.md",
		"0010-task-scoped-runtime-execution-safety.md",
		"0011-runtime-task-execution-request.md",
		"0014-llm-drafting-in-runtime-v1.md",
	} {
		adrSummaries[name] = readOptional(filepath.Join(root, "docs", "adr", name), 3000)
	}
	return LLMPayload{
		Mode:              mode,
		ParentPath:        artifact.RelPath,
		ParentArtifact:    artifact,
		ParentBody:        doc.Body,
		ContextSummary:    contextSummary,
		ADRSummaries:      adrSummaries,
		RuntimeTaskTmpl:   readOptional(filepath.Join(root, "templates", "runtime-task.md"), 5000),
		ResultSummary:     resultSummary,
		RuntimeLogRefs:    artifact.RuntimeLogRefs,
		ExcludedDataNotes: []string{"Private Runtime Log contents are not included by default.", "Project source files are not included by default.", "External connectors such as email, calendar, browser history, and chat are out of scope."},
	}, nil
}

func CreateDraftRuntimeTask(ctx context.Context, root, parentPath string, cfg Config, client LLMClient) (string, error) {
	if client == nil {
		client = OpenAICompatibleClient{}
	}
	if _, err := featureDir(root, parentPath); err != nil {
		return "", err
	}
	payload, err := BuildLLMPayload(root, parentPath)
	if err != nil {
		return "", err
	}
	if !isAllowedDraftParent(payload.ParentArtifact) {
		return "", fmt.Errorf("%s is not a ready-for-agent issue, approved plan, or failed runtime_task", payload.ParentPath)
	}
	draft, err := client.DraftRuntimeTask(ctx, cfg.LLM, payload)
	if err != nil {
		return "", err
	}
	return WriteDraftRuntimeTask(root, parentPath, payload, draft)
}

func isAllowedDraftParent(a Artifact) bool {
	return isDraftOpportunity(a) || (a.Type == "runtime_task" && a.Status == "failed")
}

func WriteDraftRuntimeTask(root, parentPath string, payload LLMPayload, draft DraftResponse) (string, error) {
	if err := validateDraftResponse(draft); err != nil {
		return "", err
	}
	dir, err := featureDir(root, parentPath)
	if err != nil {
		return "", err
	}
	taskDir := filepath.Join(dir, "runtime-tasks")
	if err := os.MkdirAll(taskDir, 0o755); err != nil {
		return "", err
	}
	n := nextNumber(taskDir)
	target := filepath.Join(taskDir, fmt.Sprintf("%02d-%s.md", n, slugify(draft.Title)))
	specYAML, err := renderExecutionSpec(draft.ExecutionSpec)
	if err != nil {
		return "", err
	}
	parentRel := relativePath(filepath.Dir(target), parentPath)
	sourceRefs := []string{parentRel, relativePath(filepath.Dir(target), filepath.Join(root, "CONTEXT.md")), relativePath(filepath.Dir(target), filepath.Join(root, "templates", "runtime-task.md"))}
	sourceRefs = append(sourceRefs, draft.SourceRefs...)
	fields := map[string]any{
		"artifact_type":       "runtime_task",
		"title":               draft.Title,
		"status":              "draft",
		"parent_refs":         []string{parentRel},
		"approval_state":      "draft",
		"approval_refs":       []string{},
		"risk_level":          "medium",
		"source_refs":         sourceRefs,
		"confidence":          "medium",
		"runtime_log_refs":    []string{},
		"sent_at":             nil,
		"late_supplement_for": nil,
		"feedback_source":     nil,
		"target_artifact":     nil,
	}
	body := renderRuntimeTaskBody(draft, specYAML, parentRel, payload.Mode)
	doc := Document{Path: target, Fields: fields, Body: body}
	if err := WriteDocument(doc); err != nil {
		return "", err
	}
	return target, nil
}

func renderRuntimeTaskBody(draft DraftResponse, specYAML, parentRel, mode string) string {
	var b strings.Builder
	fmt.Fprintf(&b, "# Runtime Task: %s\n\n", draft.Title)
	b.WriteString("## Parent\n\n")
	fmt.Fprintf(&b, "`%s`\n\n", parentRel)
	b.WriteString("This Runtime Task is an execution request and does not replace the parent artifact.\n\n")
	b.WriteString("## Goal\n\n")
	b.WriteString(strings.TrimSpace(draft.Goal) + "\n\n")
	b.WriteString("## Execution Spec\n\n")
	b.WriteString("```yaml\n")
	b.WriteString(specYAML)
	b.WriteString("\n```\n\n")
	b.WriteString("## Approval\n\n")
	b.WriteString("Approval Record pending. This draft is not executable until `approval_state: approved` and `approval_refs` point to a durable Approval Record.\n\n")
	b.WriteString("## Result\n\n")
	b.WriteString("No execution has run yet.\n\n")
	b.WriteString("## Repair Plan\n\n")
	if mode == "repair" {
		b.WriteString("This draft was generated as a follow-up proposal from a failed Runtime Task. It still requires human approval before execution.\n\n")
	} else {
		b.WriteString("If execution fails, `paos draft <failed-task>` may create a follow-up draft Runtime Task. It must not directly edit files or retry automatically.\n\n")
	}
	b.WriteString("## Comments\n\n")
	fmt.Fprintf(&b, "- Drafted by `paos draft` at `%s`.\n", time.Now().UTC().Format(time.RFC3339))
	for _, risk := range draft.Risks {
		fmt.Fprintf(&b, "- Risk: %s\n", risk)
	}
	for _, comment := range draft.Comments {
		fmt.Fprintf(&b, "- %s\n", comment)
	}
	return b.String()
}

func readOptional(path string, maxBytes int) string {
	data, err := os.ReadFile(path)
	if err != nil {
		return ""
	}
	if maxBytes > 0 && len(data) > maxBytes {
		data = data[:maxBytes]
	}
	return string(data)
}
