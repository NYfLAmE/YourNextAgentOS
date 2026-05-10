package paos

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestScanControlPlaneArtifacts(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, ".scratch/feature/issues/01-ready.md", `---
artifact_type: issue
title: Ready Issue
status: ready-for-agent
category: enhancement
approval_state: draft
---
# Issue
`)
	writeFixture(t, root, ".scratch/feature/runtime-tasks/01-task.md", `---
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
	writeFixture(t, root, ".scratch/feature/approvals/01-approval.md", `---
artifact_type: approval_record
title: Approval
status: approved
runtime_task_ref: ../runtime-tasks/01-task.md
---
# Approval
`)
	result, err := ScanControlPlane(root)
	if err != nil {
		t.Fatal(err)
	}
	if result.TypeCounts["issue"] != 1 || result.TypeCounts["runtime_task"] != 1 || result.TypeCounts["approval_record"] != 1 {
		t.Fatalf("unexpected type counts: %#v", result.TypeCounts)
	}
	if len(result.DraftOpportunities) != 1 || !strings.Contains(result.DraftOpportunities[0].RelPath, "01-ready.md") {
		t.Fatalf("unexpected draft opportunities: %#v", result.DraftOpportunities)
	}
	if len(result.Warnings) != 0 {
		t.Fatalf("unexpected warnings: %#v", result.Warnings)
	}
}

func TestScanReportsBrokenRefs(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, ".scratch/feature/runtime-tasks/01-task.md", `---
artifact_type: runtime_task
title: Broken Task
status: ready
parent_refs:
  - ../issues/missing.md
approval_state: approved
approval_refs: []
runtime_log_refs: []
---
# Runtime Task
`)
	result, err := ScanControlPlane(root)
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Warnings) < 2 {
		t.Fatalf("expected broken parent and missing approval warnings: %#v", result.Warnings)
	}
}

func writeFixture(t *testing.T, root, rel, content string) string {
	t.Helper()
	path := filepath.Join(root, filepath.FromSlash(rel))
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	return path
}
