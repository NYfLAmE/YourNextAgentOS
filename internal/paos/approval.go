package paos

import (
	"fmt"
	"os/user"
	"path/filepath"
	"strings"
	"time"
)

func ApproveRuntimeTask(root, taskPath, approver string, now time.Time) (string, error) {
	doc, err := ReadDocument(taskPath)
	if err != nil {
		return "", err
	}
	if fieldString(doc.Fields, "artifact_type") != "runtime_task" {
		return "", fmt.Errorf("%s is not a runtime_task", taskPath)
	}
	spec, err := extractExecutionSpec(doc.Body)
	if err != nil {
		return "", err
	}
	if err := validateExecutionSpec(spec); err != nil {
		return "", err
	}
	if approver == "" {
		approver = currentUsername()
	}
	if now.IsZero() {
		now = time.Now().UTC()
	}
	dir, err := featureDir(root, taskPath)
	if err != nil {
		return "", err
	}
	approvalDir := filepath.Join(dir, "approvals")
	id := now.UTC().Format("20060102T150405Z") + "-" + slugify(fieldString(doc.Fields, "title"))
	approvalPath := filepath.Join(approvalDir, id+".md")
	taskRel := relativePath(filepath.Dir(approvalPath), taskPath)
	specYAML, err := renderExecutionSpec(spec)
	if err != nil {
		return "", err
	}
	fields := map[string]any{
		"artifact_type":       "approval_record",
		"title":               "Approve " + fieldString(doc.Fields, "title"),
		"status":              "approved",
		"approved_at":         now.UTC().Format(time.RFC3339),
		"approved_by":         approver,
		"runtime_task_ref":    taskRel,
		"approval_scope":      []string{"runtime_task", "execution_workspace", "command_list", "env_profile", "network_intent", "private_runtime_log"},
		"source_refs":         []string{taskRel, relativePath(filepath.Dir(approvalPath), filepath.Join(root, "templates", "approval-record.md"))},
		"confidence":          "medium",
		"risk_level":          "medium",
		"sent_at":             nil,
		"late_supplement_for": nil,
		"feedback_source":     nil,
		"target_artifact":     nil,
	}
	body := renderApprovalBody(fields["title"].(string), taskRel, specYAML)
	if err := WriteDocument(Document{Path: approvalPath, Fields: fields, Body: body}); err != nil {
		return "", err
	}
	approvalRel := relativePath(filepath.Dir(taskPath), approvalPath)
	doc.Fields["status"] = "ready"
	doc.Fields["approval_state"] = "approved"
	appendUniqueString(doc.Fields, "approval_refs", approvalRel)
	doc.Body = replaceSection(doc.Body, "Approval", fmt.Sprintf("- Approved by `%s` at `%s`.\n- Approval Record: `%s`", approver, now.UTC().Format(time.RFC3339), approvalRel))
	if err := WriteDocument(doc); err != nil {
		return "", err
	}
	return approvalPath, nil
}

func renderApprovalBody(title, taskRel, specYAML string) string {
	var b strings.Builder
	fmt.Fprintf(&b, "# Approval Record: %s\n\n", title)
	b.WriteString("## Runtime Task\n\n")
	fmt.Fprintf(&b, "`%s`\n\n", taskRel)
	b.WriteString("## Approved Boundary\n\n")
	b.WriteString("```yaml\n")
	b.WriteString(specYAML)
	b.WriteString("\n```\n\n")
	b.WriteString("## Conditions\n\n")
	b.WriteString("- The Runtime may execute only the approved Command List.\n")
	b.WriteString("- The Runtime may write only inside the approved Execution Workspace.\n")
	b.WriteString("- The Runtime must write full logs to the Private Runtime Log and link references back to the Runtime Task.\n")
	b.WriteString("- If execution fails, LLM repair may create a draft Runtime Task but must not directly change files.\n\n")
	b.WriteString("## Evidence\n\n")
	b.WriteString("- The linked Runtime Task contains the approved Execution Workspace, Command List, Env Profile, Network Intent, and Private Runtime Log policy.\n\n")
	b.WriteString("## Comments\n\n")
	return b.String()
}

func currentUsername() string {
	if u, err := user.Current(); err == nil && u.Username != "" {
		return u.Username
	}
	return "local-user"
}
