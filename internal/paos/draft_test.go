package paos

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type fakeLLM struct {
	response DraftResponse
	err      error
	payload  LLMPayload
}

func (f *fakeLLM) DraftRuntimeTask(ctx context.Context, cfg LLMConfig, payload LLMPayload) (DraftResponse, error) {
	f.payload = payload
	return f.response, f.err
}

func TestCreateDraftRuntimeTaskFromReadyIssue(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
approval_state: draft
---
# Issue

Run documentation checks.
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	taskPath, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(filepath.ToSlash(taskPath), ".scratch/feature/runtime-tasks/01-") {
		t.Fatalf("unexpected task path: %s", taskPath)
	}
	doc, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if fieldString(doc.Fields, "status") != "draft" || fieldString(doc.Fields, "approval_state") != "draft" {
		t.Fatalf("unexpected task fields: %#v", doc.Fields)
	}
	if len(fieldStringSlice(doc.Fields, "parent_refs")) != 1 {
		t.Fatalf("expected parent ref: %#v", doc.Fields)
	}
	if client.payload.Mode != "parent" {
		t.Fatalf("expected parent payload, got %s", client.payload.Mode)
	}
}

func TestCreateDraftRuntimeTaskRefusesUnreadyParentBeforeLLMCall(t *testing.T) {
	root := t.TempDir()
	parent := writeFixture(t, root, ".scratch/feature/issues/01-draft.md", `---
artifact_type: issue
title: Draft Issue
status: needs-triage
category: enhancement
approval_state: draft
---
# Issue
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	if _, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client); err == nil {
		t.Fatal("expected unready parent to be rejected")
	}
	if client.payload.ParentPath != "" {
		t.Fatalf("LLM was called before parent readiness validation: %#v", client.payload)
	}
}

func TestParseDraftResponseRejectsMalformedOutput(t *testing.T) {
	if _, err := parseDraftResponse("```json\n{}\n```"); err == nil {
		t.Fatal("expected Markdown-fenced output to fail strict JSON parsing")
	}
	if _, err := parseDraftResponse(`{"title":"x","goal":"y","execution_spec":{"execution_workspace":{"repo":".","mode":"dedicated_worktree"},"command_list":[],"env_profile":{"mode":"empty","allow":[]},"network_intent":{"enabled":true,"reason":"test"},"private_runtime_log":{"storage":"private_runtime_directory","retention":"long_term","redaction":"none"}}}`); err == nil {
		t.Fatal("expected empty command_list to fail validation")
	}
}

func TestRepairPayloadExcludesPrivateLogContents(t *testing.T) {
	root := t.TempDir()
	secretLog := filepath.Join(root, "private-runtime-log.json")
	if err := os.WriteFile(secretLog, []byte("SECRET_LOG_CONTENT"), 0o600); err != nil {
		t.Fatal(err)
	}
	failedTask := writeFixture(t, root, ".scratch/feature/runtime-tasks/01-failed.md", `---
artifact_type: runtime_task
title: Failed Task
status: failed
parent_refs:
  - ../issues/01-ready.md
approval_state: approved
approval_refs:
  - ../approvals/01-approval.md
runtime_log_refs:
  - `+secretLog+`
---
# Runtime Task

## Result

- Runtime finished with failed.
`)
	payload, err := BuildLLMPayload(root, failedTask)
	if err != nil {
		t.Fatal(err)
	}
	rendered := renderLLMPayload(payload)
	if payload.Mode != "repair" {
		t.Fatalf("expected repair payload, got %s", payload.Mode)
	}
	if strings.Contains(rendered, "SECRET_LOG_CONTENT") {
		t.Fatalf("payload included private log contents:\n%s", rendered)
	}
	if !strings.Contains(rendered, secretLog) {
		t.Fatalf("payload should include log ref, got:\n%s", rendered)
	}
}

func validDraftResponse(root string) DraftResponse {
	return DraftResponse{
		Title: "Run documentation validation",
		Goal:  "Validate Markdown and Git diff whitespace.",
		ExecutionSpec: ExecutionSpec{
			ExecutionWorkspace: ExecutionWorkspace{Repo: ".", Mode: "dedicated_worktree", WorktreeRoot: "private_runtime_config"},
			CommandList: []CommandSpec{
				{ID: "diff-check", Command: "git diff --check", AllowedArgs: map[string]any{}, Repeatable: true},
			},
			EnvProfile:        EnvProfile{Mode: "empty", Allow: []string{}},
			NetworkIntent:     NetworkIntent{Enabled: false, Reason: "local validation only"},
			PrivateRuntimeLog: PrivateRuntimeLog{Storage: "private_runtime_directory", Retention: "long_term", Redaction: "none"},
		},
	}
}
