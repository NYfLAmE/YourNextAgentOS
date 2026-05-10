package paos

import (
	"bytes"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestRunCLIScanLeavesGitStatusUnchanged(t *testing.T) {
	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git not available")
	}
	root := t.TempDir()
	initCommittedRepo(t, root)
	writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
approval_state: draft
---
# Issue
`)
	runGit(t, root, "add", ".scratch/feature/issues/01-ready.md")
	runGit(t, root, "commit", "-m", "add issue")
	before := gitStatus(t, root)
	var out bytes.Buffer
	if err := RunCLI(t.Context(), []string{"--root", root, "scan"}, &out, &bytes.Buffer{}, nil); err != nil {
		t.Fatal(err)
	}
	after := gitStatus(t, root)
	if before != after {
		t.Fatalf("scan changed git status: before=%q after=%q output=%s", before, after, out.String())
	}
}

func TestRunCLIWatchOnceOnlyReportsControlPlaneState(t *testing.T) {
	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git not available")
	}
	root := t.TempDir()
	initCommittedRepo(t, root)
	writeFixture(t, root, ".scratch/feature/runtime-tasks/01-draft.md", `---
artifact_type: runtime_task
title: Draft Task
status: draft
parent_refs:
  - ../issues/01-ready.md
approval_state: draft
approval_refs: []
runtime_log_refs: []
---
# Runtime Task
`)
	runGit(t, root, "add", ".scratch/feature/runtime-tasks/01-draft.md")
	runGit(t, root, "commit", "-m", "add runtime task")
	before := gitStatus(t, root)
	client := &fakeLLM{response: validDraftResponse(root)}
	var out bytes.Buffer
	if err := RunCLI(t.Context(), []string{"--root", root, "watch", "--once"}, &out, &bytes.Buffer{}, client); err != nil {
		t.Fatal(err)
	}
	if client.payload.ParentPath != "" {
		t.Fatalf("watch unexpectedly called LLM: %#v", client.payload)
	}
	after := gitStatus(t, root)
	if before != after {
		t.Fatalf("watch changed git status: before=%q after=%q output=%s", before, after, out.String())
	}
	if !strings.Contains(out.String(), "draft_tasks: 1") {
		t.Fatalf("watch output did not report draft task:\n%s", out.String())
	}
}

func TestRunCLIDraftCreatesTaskWithoutProjectSourcePayload(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "CONTEXT.md", "# Context\n")
	writeFixture(t, root, "templates/runtime-task.md", "# Template\n")
	writeFixture(t, root, "internal/source.go", "package internal\nconst secretSourceMarker = \"SOURCE_MARKER_SHOULD_NOT_LEAVE_SOURCE\"\n")
	parent := writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
approval_state: draft
---
# Issue

Run safe validation.
`)
	configPath := writeFixture(t, root, "private-config.yaml", `
runtime_dir: /tmp/paos-runtime
worktree_root: /tmp/paos-worktrees
llm:
  base_url: http://127.0.0.1:1/v1
  model: test-model
  api_key_env: PAOS_TEST_API_KEY
`)
	t.Setenv("PAOS_TEST_API_KEY", "test-secret")
	client := &fakeLLM{response: validDraftResponse(root)}
	var out bytes.Buffer
	if err := RunCLI(t.Context(), []string{"--root", root, "--config", configPath, "draft", repoRel(root, parent)}, &out, &bytes.Buffer{}, client); err != nil {
		t.Fatal(err)
	}
	rendered := renderLLMPayload(client.payload)
	if strings.Contains(rendered, "SOURCE_MARKER_SHOULD_NOT_LEAVE_SOURCE") {
		t.Fatalf("draft payload included project source content:\n%s", rendered)
	}
	if !strings.Contains(out.String(), "created_runtime_task: .scratch/feature/runtime-tasks/01-") {
		t.Fatalf("unexpected draft output:\n%s", out.String())
	}
}

func initCommittedRepo(t *testing.T, root string) {
	t.Helper()
	runGit(t, root, "init")
	runGit(t, root, "config", "user.email", "test@example.invalid")
	runGit(t, root, "config", "user.name", "Test User")
	if err := os.WriteFile(filepath.Join(root, "README.md"), []byte("# Test\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	runGit(t, root, "add", "README.md")
	runGit(t, root, "commit", "-m", "init")
}

func gitStatus(t *testing.T, root string) string {
	t.Helper()
	cmd := exec.Command("git", "status", "--short")
	cmd.Dir = root
	out, err := cmd.Output()
	if err != nil {
		t.Fatal(err)
	}
	return string(out)
}
