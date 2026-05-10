package paos

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func Main(ctx context.Context, args []string, stdout, stderr io.Writer) int {
	if err := RunCLI(ctx, args, stdout, stderr, nil); err != nil {
		fmt.Fprintln(stderr, "paos:", err)
		return 1
	}
	return 0
}

func RunCLI(ctx context.Context, args []string, stdout, stderr io.Writer, client LLMClient) error {
	root, err := os.Getwd()
	if err != nil {
		return err
	}
	configPath := DefaultConfigPath()
	args, err = parseGlobalFlags(args, &root, &configPath)
	if err != nil {
		return err
	}
	if len(args) == 0 {
		printUsage(stdout)
		return nil
	}
	cmd := args[0]
	args = args[1:]
	switch cmd {
	case "help", "-h", "--help":
		printUsage(stdout)
		return nil
	case "scan":
		return cmdScan(root, stdout)
	case "status":
		return cmdStatus(root, configPath, stdout)
	case "draft":
		return cmdDraft(ctx, root, configPath, args, stdout, client)
	case "approve":
		return cmdApprove(root, args, stdout)
	case "run":
		return cmdRun(ctx, root, configPath, args, stdout)
	case "watch":
		return cmdWatch(ctx, root, args, stdout)
	default:
		return fmt.Errorf("unknown command %q", cmd)
	}
}

func parseGlobalFlags(args []string, root, configPath *string) ([]string, error) {
	out := []string{}
	for i := 0; i < len(args); i++ {
		arg := args[i]
		switch arg {
		case "--root":
			i++
			if i >= len(args) {
				return nil, errors.New("--root requires a value")
			}
			*root = filepath.Clean(args[i])
		case "--config":
			i++
			if i >= len(args) {
				return nil, errors.New("--config requires a value")
			}
			*configPath = filepath.Clean(args[i])
		default:
			out = append(out, arg)
		}
	}
	return out, nil
}

func printUsage(w io.Writer) {
	fmt.Fprintln(w, `paos - Personal Agent OS Runtime CLI

Usage:
  paos [--root <repo>] [--config <path>] scan
  paos [--root <repo>] [--config <path>] status
  paos [--root <repo>] [--config <path>] draft <parent>
  paos [--root <repo>] approve [--approver <name>] <runtime-task>
  paos [--root <repo>] [--config <path>] run <runtime-task>
  paos [--root <repo>] watch [--once] [--interval <duration>]

Commands:
  scan     Read-only reconciliation of .scratch Control Plane artifacts.
  status   Report config discovery, draft opportunities, task states, and recent results.
  draft    Use configured OpenAI-compatible LLM to create a draft Runtime Task.
  approve  Create an Approval Record and move a complete Runtime Task to ready.
  run      Execute an approved Runtime Task command list in a dedicated worktree.
  watch    Poll local Control Plane paths and surface scan/status output; it does not draft, approve, or run.`)
}

func cmdScan(root string, stdout io.Writer) error {
	result, err := ScanControlPlane(root)
	if err != nil {
		return err
	}
	printScanResult(stdout, result)
	return nil
}

func cmdStatus(root, configPath string, stdout io.Writer) error {
	cfg, found, err := LoadConfig(configPath)
	if err != nil {
		return err
	}
	fmt.Fprintf(stdout, "config_path: %s\n", configPath)
	fmt.Fprintf(stdout, "config_found: %t\n", found)
	fmt.Fprintf(stdout, "runtime_dir: %s\n", cfg.RuntimeDir)
	fmt.Fprintf(stdout, "worktree_root: %s\n", cfg.WorktreeRoot)
	fmt.Fprintf(stdout, "llm.base_url configured: %t\n", cfg.LLM.BaseURL != "")
	fmt.Fprintf(stdout, "llm.model configured: %t\n", cfg.LLM.Model != "")
	fmt.Fprintf(stdout, "llm.api_key_env configured: %t\n", cfg.LLM.APIKeyEnv != "")
	result, err := ScanControlPlane(root)
	if err != nil {
		return err
	}
	printStatus(stdout, result)
	return nil
}

func cmdDraft(ctx context.Context, root, configPath string, args []string, stdout io.Writer, client LLMClient) error {
	if len(args) != 1 {
		return errors.New("draft requires <parent>")
	}
	cfg, found, err := LoadConfig(configPath)
	if err != nil {
		return err
	}
	if !found {
		return fmt.Errorf("config not found at %s", configPath)
	}
	parent := resolveCLIPath(root, args[0])
	taskPath, err := CreateDraftRuntimeTask(ctx, root, parent, cfg, client)
	if err != nil {
		return err
	}
	fmt.Fprintf(stdout, "created_runtime_task: %s\n", repoRel(root, taskPath))
	return nil
}

func cmdApprove(root string, args []string, stdout io.Writer) error {
	fs := flag.NewFlagSet("approve", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	approver := fs.String("approver", "", "approver name")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if fs.NArg() != 1 {
		return errors.New("approve requires <runtime-task>")
	}
	task := resolveCLIPath(root, fs.Arg(0))
	approvalPath, err := ApproveRuntimeTask(root, task, *approver, time.Now().UTC())
	if err != nil {
		return err
	}
	fmt.Fprintf(stdout, "created_approval_record: %s\n", repoRel(root, approvalPath))
	return nil
}

func cmdRun(ctx context.Context, root, configPath string, args []string, stdout io.Writer) error {
	if len(args) != 1 {
		return errors.New("run requires <runtime-task>")
	}
	cfg, _, err := LoadConfig(configPath)
	if err != nil {
		return err
	}
	task := resolveCLIPath(root, args[0])
	err = RunRuntimeTask(ctx, root, task, cfg, time.Now().UTC())
	if err != nil {
		return err
	}
	fmt.Fprintf(stdout, "runtime_task_succeeded: %s\n", repoRel(root, task))
	return nil
}

func cmdWatch(ctx context.Context, root string, args []string, stdout io.Writer) error {
	fs := flag.NewFlagSet("watch", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	once := fs.Bool("once", false, "run one reconciliation and exit")
	interval := fs.Duration("interval", 2*time.Second, "poll interval")
	if err := fs.Parse(args); err != nil {
		return err
	}
	for {
		result, err := ScanControlPlane(root)
		if err != nil {
			return err
		}
		fmt.Fprintf(stdout, "watch_tick: %s\n", time.Now().UTC().Format(time.RFC3339))
		printStatus(stdout, result)
		if *once {
			return nil
		}
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(*interval):
		}
	}
}

func resolveCLIPath(root, value string) string {
	if filepath.IsAbs(value) {
		return filepath.Clean(value)
	}
	return filepath.Join(root, filepath.FromSlash(value))
}

func printScanResult(w io.Writer, result ScanResult) {
	fmt.Fprintf(w, "artifacts: %d\n", len(result.Artifacts))
	fmt.Fprintln(w, "artifact_types:")
	for _, key := range sortedMapKeys(result.TypeCounts) {
		fmt.Fprintf(w, "  %s: %d\n", key, result.TypeCounts[key])
	}
	fmt.Fprintln(w, "statuses:")
	for _, key := range sortedMapKeys(result.StatusCounts) {
		fmt.Fprintf(w, "  %s: %d\n", key, result.StatusCounts[key])
	}
	fmt.Fprintln(w, "draft_opportunities:")
	for _, a := range result.DraftOpportunities {
		fmt.Fprintf(w, "  - %s [%s/%s]\n", a.RelPath, a.Type, a.Status)
	}
	fmt.Fprintln(w, "runtime_tasks:")
	for _, a := range result.Artifacts {
		if a.Type == "runtime_task" {
			fmt.Fprintf(w, "  - %s status=%s approval_state=%s\n", a.RelPath, a.Status, a.ApprovalState)
		}
	}
	printWarnings(w, result.Warnings)
}

func printStatus(w io.Writer, result ScanResult) {
	fmt.Fprintf(w, "pending_draft_opportunities: %d\n", len(result.DraftOpportunities))
	for _, a := range result.DraftOpportunities {
		fmt.Fprintf(w, "  - %s\n", a.RelPath)
	}
	buckets := map[string][]Artifact{
		"draft_tasks":          {},
		"ready_tasks":          {},
		"running_tasks":        {},
		"blocked_failed_tasks": {},
		"recent_results":       {},
	}
	for _, a := range result.Artifacts {
		if a.Type != "runtime_task" {
			continue
		}
		switch a.Status {
		case "draft":
			buckets["draft_tasks"] = append(buckets["draft_tasks"], a)
		case "ready":
			buckets["ready_tasks"] = append(buckets["ready_tasks"], a)
		case "running":
			buckets["running_tasks"] = append(buckets["running_tasks"], a)
		case "blocked", "failed":
			buckets["blocked_failed_tasks"] = append(buckets["blocked_failed_tasks"], a)
		case "succeeded", "cancelled":
			buckets["recent_results"] = append(buckets["recent_results"], a)
		}
	}
	for _, name := range []string{"draft_tasks", "ready_tasks", "running_tasks", "blocked_failed_tasks", "recent_results"} {
		fmt.Fprintf(w, "%s: %d\n", name, len(buckets[name]))
		for _, a := range buckets[name] {
			fmt.Fprintf(w, "  - %s status=%s approval_state=%s\n", a.RelPath, a.Status, a.ApprovalState)
		}
	}
	printWarnings(w, result.Warnings)
}

func printWarnings(w io.Writer, warnings []string) {
	if len(warnings) == 0 {
		fmt.Fprintln(w, "warnings: 0")
		return
	}
	fmt.Fprintf(w, "warnings: %d\n", len(warnings))
	for _, warning := range warnings {
		fmt.Fprintf(w, "  - %s\n", warning)
	}
}

func commandName(args []string) string {
	if len(args) == 0 {
		return ""
	}
	return strings.TrimSpace(args[0])
}
