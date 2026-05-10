package paos

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
)

func ScanControlPlane(root string) (ScanResult, error) {
	root = filepath.Clean(root)
	scratch := filepath.Join(root, ".scratch")
	result := ScanResult{
		StatusCounts: map[string]int{},
		TypeCounts:   map[string]int{},
	}
	if _, err := os.Stat(scratch); os.IsNotExist(err) {
		return result, nil
	}
	err := filepath.WalkDir(scratch, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			result.Warnings = append(result.Warnings, fmt.Sprintf("walk %s: %v", path, err))
			return nil
		}
		if d.IsDir() {
			return nil
		}
		if filepath.Ext(path) != ".md" {
			return nil
		}
		doc, err := ReadDocument(path)
		if err != nil {
			result.Warnings = append(result.Warnings, fmt.Sprintf("parse %s: %v", repoRel(root, path), err))
			return nil
		}
		typ := fieldString(doc.Fields, "artifact_type")
		if typ == "" {
			return nil
		}
		artifact := Artifact{
			Path:           path,
			RelPath:        repoRel(root, path),
			Type:           typ,
			Title:          fieldString(doc.Fields, "title"),
			Status:         fieldString(doc.Fields, "status"),
			Category:       fieldString(doc.Fields, "category"),
			ApprovalState:  fieldString(doc.Fields, "approval_state"),
			ParentRefs:     fieldStringSlice(doc.Fields, "parent_refs"),
			ApprovalRefs:   fieldStringSlice(doc.Fields, "approval_refs"),
			RuntimeLogRefs: fieldStringSlice(doc.Fields, "runtime_log_refs"),
		}
		result.Artifacts = append(result.Artifacts, artifact)
		result.TypeCounts[artifact.Type]++
		result.StatusCounts[artifact.Status]++
		if isDraftOpportunity(artifact) {
			result.DraftOpportunities = append(result.DraftOpportunities, artifact)
		}
		checkRefs(&result, artifact, "parent_refs", artifact.ParentRefs)
		checkRefs(&result, artifact, "approval_refs", artifact.ApprovalRefs)
		if artifact.Type == "runtime_task" {
			if len(artifact.ParentRefs) == 0 {
				result.Warnings = append(result.Warnings, fmt.Sprintf("%s: runtime_task has no parent_refs", artifact.RelPath))
			}
			if artifact.ApprovalState == "approved" && len(artifact.ApprovalRefs) == 0 {
				result.Warnings = append(result.Warnings, fmt.Sprintf("%s: approved runtime_task has no approval_refs", artifact.RelPath))
			}
		}
		return nil
	})
	sort.Slice(result.Artifacts, func(i, j int) bool {
		return result.Artifacts[i].RelPath < result.Artifacts[j].RelPath
	})
	sort.Slice(result.DraftOpportunities, func(i, j int) bool {
		return result.DraftOpportunities[i].RelPath < result.DraftOpportunities[j].RelPath
	})
	sort.Strings(result.Warnings)
	return result, err
}

func isDraftOpportunity(a Artifact) bool {
	if a.Type == "issue" && a.Status == "ready-for-agent" {
		return true
	}
	if (a.Type == "plan" || a.Type == "prd") && a.ApprovalState == "approved" && a.Status != "cancelled" {
		return true
	}
	return false
}

func checkRefs(result *ScanResult, artifact Artifact, field string, refs []string) {
	for _, ref := range refs {
		if ref == "" {
			continue
		}
		if _, err := os.Stat(resolveRef(artifact.Path, ref)); err != nil {
			result.Warnings = append(result.Warnings, fmt.Sprintf("%s: broken %s entry %q", artifact.RelPath, field, ref))
		}
	}
}
