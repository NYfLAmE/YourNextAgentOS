package paos

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestApproveRuntimeTaskCreatesRecordAndMarksReady(t *testing.T) {
	root := t.TempDir()
	taskPath := writeRuntimeTaskFixture(t, root, ".scratch/feature/runtime-tasks/01-doc-check.md", "ready-doc-check", true)
	approvalPath, err := ApproveRuntimeTask(root, taskPath, "tester", time.Date(2026, 5, 10, 1, 2, 3, 0, time.UTC))
	if err != nil {
		t.Fatal(err)
	}
	approval, err := ReadDocument(approvalPath)
	if err != nil {
		t.Fatal(err)
	}
	if fieldString(approval.Fields, "artifact_type") != "approval_record" || fieldString(approval.Fields, "approved_by") != "tester" {
		t.Fatalf("unexpected approval fields: %#v", approval.Fields)
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if fieldString(task.Fields, "status") != "ready" || fieldString(task.Fields, "approval_state") != "approved" {
		t.Fatalf("task was not marked ready/approved: %#v", task.Fields)
	}
	if len(fieldStringSlice(task.Fields, "approval_refs")) != 1 {
		t.Fatalf("expected approval ref: %#v", task.Fields)
	}
}

func TestApproveRuntimeTaskRejectsMissingCommandList(t *testing.T) {
	root := t.TempDir()
	taskPath := writeRuntimeTaskFixture(t, root, ".scratch/feature/runtime-tasks/01-empty.md", "empty", false)
	if _, err := ApproveRuntimeTask(root, taskPath, "tester", time.Now()); err == nil {
		t.Fatal("expected approval to reject empty command_list")
	}
}

func TestRunRuntimeTaskExecutesApprovedCommandAndWritesPrivateLog(t *testing.T) {
	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git not available")
	}
	root := t.TempDir()
	runGit(t, root, "init")
	runGit(t, root, "config", "user.email", "test@example.invalid")
	runGit(t, root, "config", "user.name", "Test User")
	if err := os.WriteFile(filepath.Join(root, "README.md"), []byte("# Test\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	runGit(t, root, "add", "README.md")
	runGit(t, root, "commit", "-m", "init")
	writeFixture(t, root, ".scratch/feature/issues/01-parent.md", `---
artifact_type: issue
title: Parent
status: ready-for-agent
approval_state: draft
---
# Parent

## Comments
`)
	taskPath := writeRuntimeTaskFixture(t, root, ".scratch/feature/runtime-tasks/01-doc-check.md", "doc-check", true)
	_, err := ApproveRuntimeTask(root, taskPath, "tester", time.Date(2026, 5, 10, 1, 2, 3, 0, time.UTC))
	if err != nil {
		t.Fatal(err)
	}
	cfg := Config{RuntimeDir: filepath.Join(root, ".private-runtime"), WorktreeRoot: filepath.Join(root, ".private-runtime", "worktrees")}
	err = RunRuntimeTask(t.Context(), root, taskPath, cfg, time.Date(2026, 5, 10, 1, 3, 0, 0, time.UTC))
	if err != nil {
		t.Fatal(err)
	}
	task, err := ReadDocument(taskPath)
	if err != nil {
		t.Fatal(err)
	}
	if fieldString(task.Fields, "status") != "succeeded" {
		t.Fatalf("expected succeeded, got %#v", task.Fields)
	}
	refs := fieldStringSlice(task.Fields, "runtime_log_refs")
	if len(refs) != 1 {
		t.Fatalf("expected one log ref, got %#v", refs)
	}
	logBytes, err := os.ReadFile(refs[0])
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(logBytes), `"stdout": "ok`) {
		t.Fatalf("expected full stdout in private log, got:\n%s", string(logBytes))
	}
	if strings.Contains(task.Body, `"stdout"`) {
		t.Fatalf("task body should not paste full private stdout:\n%s", task.Body)
	}
	parent, err := os.ReadFile(filepath.Join(root, ".scratch/feature/issues/01-parent.md"))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(parent), "Private Runtime Log refs are linked from the Runtime Task") {
		t.Fatalf("parent summary missing:\n%s", string(parent))
	}
}

func writeRuntimeTaskFixture(t *testing.T, root, rel, title string, includeCommand bool) string {
	t.Helper()
	commandList := "command_list: []"
	if includeCommand {
		commandList = `command_list:
  - id: echo-ok
    command: printf 'ok\n'
    allowed_args: {}
    repeatable: true`
	}
	return writeFixture(t, root, rel, `---
artifact_type: runtime_task
title: `+title+`
status: draft
parent_refs:
  - ../issues/01-parent.md
approval_state: draft
approval_refs: []
runtime_log_refs: []
---
# Runtime Task: `+title+`

## Parent

`+"`../issues/01-parent.md`"+`

## Goal

Run a safe command.

## Execution Spec

`+"```yaml"+`
execution_workspace:
  repo: .
  mode: dedicated_worktree
  worktree_root: private_runtime_config

`+commandList+`

env_profile:
  mode: empty
  allow: []

network_intent:
  enabled: false
  reason: local test only

private_runtime_log:
  storage: private_runtime_directory
  retention: long_term
  redaction: none
`+"```"+`

## Approval

Pending.

## Result

No execution has run yet.

## Comments
`)
}

func runGit(t *testing.T, dir string, args ...string) {
	t.Helper()
	cmd := exec.Command("git", args...)
	cmd.Dir = dir
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("git %v failed: %v\n%s", args, err, string(out))
	}
}
