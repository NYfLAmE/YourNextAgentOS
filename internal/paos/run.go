package paos

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

func RunRuntimeTask(ctx context.Context, root, taskPath string, cfg Config, now time.Time) error {
	doc, err := ReadDocument(taskPath)
	if err != nil {
		return err
	}
	if fieldString(doc.Fields, "artifact_type") != "runtime_task" {
		return fmt.Errorf("%s is not a runtime_task", taskPath)
	}
	if fieldString(doc.Fields, "status") != "ready" || fieldString(doc.Fields, "approval_state") != "approved" {
		return fmt.Errorf("runtime task must be status ready and approval_state approved")
	}
	approvalRefs := fieldStringSlice(doc.Fields, "approval_refs")
	if len(approvalRefs) == 0 {
		return fmt.Errorf("runtime task has no approval_refs")
	}
	spec, err := extractExecutionSpec(doc.Body)
	if err != nil {
		return err
	}
	for _, ref := range approvalRefs {
		approvalPath := resolveRef(taskPath, ref)
		approval, err := ReadDocument(approvalPath)
		if err != nil {
			return fmt.Errorf("read approval_ref %s: %w", ref, err)
		}
		if fieldString(approval.Fields, "artifact_type") != "approval_record" || fieldString(approval.Fields, "status") != "approved" {
			return fmt.Errorf("approval_ref %s is not an approved approval_record", ref)
		}
		taskRef := fieldString(approval.Fields, "runtime_task_ref")
		if taskRef == "" || filepath.Clean(resolveRef(approvalPath, taskRef)) != filepath.Clean(taskPath) {
			return fmt.Errorf("approval_ref %s does not approve this runtime task", ref)
		}
		if err := validateApprovalBoundary(approval, spec); err != nil {
			return fmt.Errorf("approval_ref %s approval boundary mismatch: %w", ref, err)
		}
	}
	if err := validateExecutionSpec(spec); err != nil {
		return err
	}
	if now.IsZero() {
		now = time.Now().UTC()
	}
	doc.Fields["status"] = "running"
	doc.Body = appendSectionNote(doc.Body, "Result", fmt.Sprintf("- Runtime started at `%s`.", now.UTC().Format(time.RFC3339)))
	if err := WriteDocument(doc); err != nil {
		return err
	}
	worktree, err := createExecutionWorktree(root, spec, cfg, taskPath, now)
	if err != nil {
		return finalizeRun(root, taskPath, doc, nil, fmt.Errorf("create execution workspace: %w", err))
	}
	logRefs, runErr := executeCommands(ctx, taskPath, worktree, spec, cfg, now)
	return finalizeRun(root, taskPath, doc, logRefs, runErr)
}

func createExecutionWorktree(root string, spec ExecutionSpec, cfg Config, taskPath string, now time.Time) (string, error) {
	repo := resolveRepo(root, filepath.Dir(taskPath), spec.ExecutionWorkspace.Repo)
	rootDir := cfg.WorktreeRoot
	if spec.ExecutionWorkspace.WorktreeRoot != "" && spec.ExecutionWorkspace.WorktreeRoot != "private_runtime_config" {
		rootDir = spec.ExecutionWorkspace.WorktreeRoot
	}
	if err := os.MkdirAll(rootDir, 0o755); err != nil {
		return "", err
	}
	title := strings.TrimSuffix(filepath.Base(taskPath), filepath.Ext(taskPath))
	worktree := filepath.Join(rootDir, now.UTC().Format("20060102T150405Z")+"-"+slugify(title))
	cmd := exec.Command("git", "-C", repo, "worktree", "add", "--detach", worktree, "HEAD")
	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("%w: %s", err, strings.TrimSpace(stderr.String()))
	}
	return worktree, nil
}

func resolveRepo(root, taskDir, repo string) string {
	repo = strings.TrimSpace(repo)
	if repo == "" || repo == "." {
		return root
	}
	if filepath.IsAbs(repo) {
		return filepath.Clean(repo)
	}
	rootCandidate := filepath.Join(root, filepath.FromSlash(repo))
	if _, err := os.Stat(rootCandidate); err == nil {
		return rootCandidate
	}
	return filepath.Join(taskDir, filepath.FromSlash(repo))
}

func executeCommands(ctx context.Context, taskPath, worktree string, spec ExecutionSpec, cfg Config, now time.Time) ([]string, error) {
	logDir := filepath.Join(cfg.RuntimeDir, "logs", slugify(strings.TrimSuffix(filepath.Base(taskPath), filepath.Ext(taskPath))), now.UTC().Format("20060102T150405Z"))
	if err := os.MkdirAll(logDir, 0o700); err != nil {
		return nil, err
	}
	var refs []string
	for _, command := range spec.CommandList {
		started := time.Now().UTC()
		cmdCtx, cancel := context.WithTimeout(ctx, 30*time.Minute)
		cmd := exec.CommandContext(cmdCtx, "bash", "-lc", command.Command)
		cmd.Dir = worktree
		cmd.Env = buildCommandEnv(spec.EnvProfile)
		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr
		runErr := cmd.Run()
		cancel()
		ended := time.Now().UTC()
		exitCode := 0
		if runErr != nil {
			exitCode = 1
			if exitErr, ok := runErr.(*exec.ExitError); ok {
				exitCode = exitErr.ExitCode()
			}
		}
		log := RunLog{
			TaskPath:        taskPath,
			CommandID:       command.ID,
			Command:         command.Command,
			Worktree:        worktree,
			StartedAt:       started,
			EndedAt:         ended,
			ExitCode:        exitCode,
			Stdout:          stdout.String(),
			Stderr:          stderr.String(),
			EnvProfileMode:  spec.EnvProfile.Mode,
			AllowedEnvNames: append([]string(nil), spec.EnvProfile.Allow...),
		}
		logPath := filepath.Join(logDir, slugify(command.ID)+".json")
		data, err := json.MarshalIndent(log, "", "  ")
		if err != nil {
			return refs, err
		}
		if err := os.WriteFile(logPath, append(data, '\n'), 0o600); err != nil {
			return refs, err
		}
		refs = append(refs, logPath)
		if runErr != nil {
			return refs, fmt.Errorf("command %s failed with exit code %d", command.ID, exitCode)
		}
	}
	return refs, nil
}

func buildCommandEnv(profile EnvProfile) []string {
	env := []string{}
	for _, name := range []string{"PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"} {
		if value, ok := os.LookupEnv(name); ok {
			env = append(env, name+"="+value)
		}
	}
	for _, name := range profile.Allow {
		name = strings.TrimSpace(name)
		if name == "" {
			continue
		}
		if value, ok := os.LookupEnv(name); ok {
			env = append(env, name+"="+value)
		}
	}
	return env
}

func finalizeRun(root, taskPath string, doc Document, logRefs []string, runErr error) error {
	fresh, err := ReadDocument(taskPath)
	if err == nil {
		doc = fresh
	}
	status := "succeeded"
	if runErr != nil {
		status = "failed"
	}
	doc.Fields["status"] = status
	for _, ref := range logRefs {
		appendUniqueString(doc.Fields, "runtime_log_refs", ref)
	}
	var note strings.Builder
	fmt.Fprintf(&note, "- Runtime finished with `%s`.", status)
	if runErr != nil {
		fmt.Fprintf(&note, "\n- Error: `%s`.", runErr.Error())
	}
	if len(logRefs) > 0 {
		note.WriteString("\n- Private Runtime Log refs:")
		for _, ref := range logRefs {
			fmt.Fprintf(&note, "\n  - `%s`", ref)
		}
	}
	doc.Body = appendSectionNote(doc.Body, "Result", note.String())
	if err := WriteDocument(doc); err != nil {
		return err
	}
	updateParentWithRunSummary(root, taskPath, doc, status, logRefs)
	if runErr != nil {
		return runErr
	}
	return nil
}

func validateApprovalBoundary(approval Document, taskSpec ExecutionSpec) error {
	approvedSpec, err := extractApprovedBoundary(approval.Body)
	if err != nil {
		return err
	}
	if err := validateExecutionSpec(approvedSpec); err != nil {
		return err
	}
	approvedYAML, err := renderExecutionSpec(approvedSpec)
	if err != nil {
		return err
	}
	taskYAML, err := renderExecutionSpec(taskSpec)
	if err != nil {
		return err
	}
	if approvedYAML != taskYAML {
		return fmt.Errorf("current Execution Spec differs from the approved boundary")
	}
	return nil
}

func updateParentWithRunSummary(root, taskPath string, taskDoc Document, status string, logRefs []string) {
	refs := fieldStringSlice(taskDoc.Fields, "parent_refs")
	if len(refs) == 0 {
		return
	}
	parentPath := resolveRef(taskPath, refs[0])
	parent, err := ReadDocument(parentPath)
	if err != nil {
		return
	}
	taskRel := relativePath(filepath.Dir(parentPath), taskPath)
	note := fmt.Sprintf("- Runtime Task `%s` finished with `%s`.", taskRel, status)
	if len(logRefs) > 0 {
		note += " Private Runtime Log refs are linked from the Runtime Task."
	}
	parent.Body = appendSectionNote(parent.Body, "Comments", note)
	_ = WriteDocument(parent)
}
