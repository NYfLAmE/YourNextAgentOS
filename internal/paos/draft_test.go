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

func TestCreateDraftRuntimeTaskIncludesSourceRefsContextPack(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	evidencePath := writeFixture(t, root, ".scratch/feature/docs/evidence.md", "EVIDENCE_MARKER\n")
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
source_refs:
  - ../docs/evidence.md
approval_state: draft
---
# Issue

Use the cited evidence.
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	taskPath, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client)
	if err != nil {
		t.Fatal(err)
	}
	renderedPayload := renderLLMPayload(client.payload)
	if !strings.Contains(renderedPayload, "EVIDENCE_MARKER") {
		t.Fatalf("payload should include source_refs content:\n%s", renderedPayload)
	}
	if !strings.Contains(renderedPayload, evidencePath) {
		t.Fatalf("payload should include absolute source ref path:\n%s", renderedPayload)
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(task.Body, "## Context Pack") || !strings.Contains(task.Body, evidencePath) || !strings.Contains(task.Body, "included") {
		t.Fatalf("draft should include Context Pack metadata:\n%s", task.Body)
	}
	if strings.Contains(task.Body, "EVIDENCE_MARKER") {
		t.Fatalf("draft should not persist source_refs content:\n%s", task.Body)
	}
}

func TestCreateDraftRuntimeTaskAllowsExplicitAbsoluteSourceRef(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	absoluteRef := writeFixture(t, root, "external-evidence.md", "ABSOLUTE_REF_MARKER\n")
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
source_refs:
  - `+absoluteRef+`
approval_state: draft
---
# Issue
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	taskPath, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client)
	if err != nil {
		t.Fatal(err)
	}
	renderedPayload := renderLLMPayload(client.payload)
	if !strings.Contains(renderedPayload, "ABSOLUTE_REF_MARKER") {
		t.Fatalf("payload should include explicit absolute source_ref:\n%s", renderedPayload)
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(task.Body, absoluteRef) || !strings.Contains(task.Body, "status=included") {
		t.Fatalf("draft should record absolute source_ref metadata:\n%s", task.Body)
	}
}

func TestCreateDraftRuntimeTaskExcludesSensitiveSourceRefs(t *testing.T) {
	root := t.TempDir()
	t.Setenv("HOME", root)
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	privateConfig := writeFixture(t, root, ".personal-agent-os/config.yaml", "PRIVATE_CONFIG_MARKER\n")
	privateLog := writeFixture(t, root, ".personal-agent-os/runtime/logs/run.json", "PRIVATE_LOG_MARKER\n")
	gitInternal := writeFixture(t, root, ".git/config", "GIT_INTERNAL_MARKER\n")
	writeFixture(t, root, ".scratch/feature/.env", "ENV_SECRET_MARKER\n")
	writeFixture(t, root, ".scratch/feature/key.pem", "PEM_SECRET_MARKER\n")
	writeFixture(t, root, ".scratch/feature/token.txt", "TOKEN_SECRET_MARKER\n")
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
source_refs:
  - `+privateConfig+`
  - `+privateLog+`
  - `+gitInternal+`
  - ../.env
  - ../key.pem
  - ../token.txt
approval_state: draft
---
# Issue
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	taskPath, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client)
	if err != nil {
		t.Fatal(err)
	}
	renderedPayload := renderLLMPayload(client.payload)
	for _, marker := range []string{"PRIVATE_CONFIG_MARKER", "PRIVATE_LOG_MARKER", "GIT_INTERNAL_MARKER", "ENV_SECRET_MARKER", "PEM_SECRET_MARKER", "TOKEN_SECRET_MARKER"} {
		if strings.Contains(renderedPayload, marker) {
			t.Fatalf("payload should not include sensitive marker %s:\n%s", marker, renderedPayload)
		}
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(task.Body, "status=excluded") || !strings.Contains(task.Body, "sensitive source_ref") {
		t.Fatalf("draft should record excluded sensitive refs:\n%s", task.Body)
	}
}

func TestCreateDraftRuntimeTaskTruncatesLargeSourceRef(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	largeContent := strings.Repeat("A", sourceRefMaxBytes) + "TAIL_MARKER_SHOULD_BE_TRUNCATED\n"
	largePath := writeFixture(t, root, ".scratch/feature/docs/large.md", largeContent)
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
source_refs:
  - `+largePath+`
approval_state: draft
---
# Issue
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	taskPath, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client)
	if err != nil {
		t.Fatal(err)
	}
	renderedPayload := renderLLMPayload(client.payload)
	if strings.Contains(renderedPayload, "TAIL_MARKER_SHOULD_BE_TRUNCATED") {
		t.Fatalf("payload should truncate large source ref:\n%s", renderedPayload)
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(task.Body, "truncated=true") {
		t.Fatalf("draft should record truncation:\n%s", task.Body)
	}
}

func TestCreateDraftRuntimeTaskExcludesBinarySourceRef(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	binaryPath := filepath.Join(root, ".scratch", "feature", "docs", "binary.dat")
	if err := os.MkdirAll(filepath.Dir(binaryPath), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(binaryPath, []byte{0xff, 0x00, 0x01}, 0o644); err != nil {
		t.Fatal(err)
	}
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
source_refs:
  - ../docs/binary.dat
approval_state: draft
---
# Issue
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	taskPath, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client)
	if err != nil {
		t.Fatal(err)
	}
	renderedPayload := renderLLMPayload(client.payload)
	if strings.Contains(renderedPayload, "content:") {
		t.Fatalf("binary source_ref should not render content:\n%s", renderedPayload)
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(task.Body, "status=excluded") || !strings.Contains(task.Body, "binary or non-UTF-8 source_ref") {
		t.Fatalf("draft should record binary exclusion:\n%s", task.Body)
	}
}

func TestCreateDraftRuntimeTaskExcludesExternalURLSourceRef(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
source_refs:
  - https://example.com/evidence.md
approval_state: draft
---
# Issue
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	taskPath, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client)
	if err != nil {
		t.Fatal(err)
	}
	renderedPayload := renderLLMPayload(client.payload)
	if strings.Contains(renderedPayload, "content:") {
		t.Fatalf("URL source_ref should not render content:\n%s", renderedPayload)
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(task.Body, "status=excluded") || !strings.Contains(task.Body, "unapproved external URL source_ref") {
		t.Fatalf("draft should record URL exclusion:\n%s", task.Body)
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

func TestCreateDraftRuntimeTaskRefusesParentOutsideScratchBeforeLLMCall(t *testing.T) {
	root := t.TempDir()
	parent := writeFixture(t, root, "outside-ready-issue.md", `---
artifact_type: issue
title: Outside Ready Issue
status: ready-for-agent
category: enhancement
approval_state: draft
---
# Issue
`)
	client := &fakeLLM{response: validDraftResponse(root)}
	if _, err := CreateDraftRuntimeTask(t.Context(), root, parent, Config{}, client); err == nil {
		t.Fatal("expected parent outside .scratch to be rejected")
	}
	if client.payload.ParentPath != "" {
		t.Fatalf("LLM was called before parent location validation: %#v", client.payload)
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
