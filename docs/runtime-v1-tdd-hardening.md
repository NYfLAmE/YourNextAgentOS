# Runtime v1 TDD Hardening

This document records the corrective TDD pass after the first `paos` Runtime v1 implementation. It is an audit artifact for future agents and reviewers: use it to understand which behaviors are now protected by tests and where the remaining gaps are.

## Why This Exists

The initial Runtime v1 implementation landed with tests, but the work did not strictly follow the intended TDD loop. The corrective pass used smaller behavior slices:

1. Write a behavior test first.
2. Confirm RED when the behavior was missing.
3. Make the smallest implementation change.
4. Re-run the focused test to confirm GREEN.
5. Add public-interface characterization tests for already-working high-risk boundaries.

Tests should protect observable Runtime behavior through `paos` CLI entrypoints or exported Runtime operations, not incidental internal structure.

## RED/GREEN Evidence

| Behavior | RED Evidence | GREEN Change |
| --- | --- | --- |
| `paos run` must reject a Runtime Task whose current `Execution Spec` differs from the approved `Approved Boundary`. | `TestRunRuntimeTaskRejectsBoundaryChangedAfterApproval` failed because the mutated command still executed. | `RunRuntimeTask` now parses the Approval Record `Approved Boundary` and compares it with the current task `Execution Spec` before creating a worktree or running commands. |
| `paos draft` must reject a parent outside `.scratch/<feature>` before reading payload or calling the LLM. | `TestCreateDraftRuntimeTaskRefusesParentOutsideScratchBeforeLLMCall` failed because the fake LLM received a payload for an outside ready issue. | `CreateDraftRuntimeTask` now validates the parent feature directory before building the LLM Payload. |

## Behavior Coverage Matrix

| Requirement / Risk Boundary | Test Coverage |
| --- | --- |
| Private config can be loaded and `paos status` does not print secret values. | `TestLoadConfigAndStatusDoesNotPrintSecret`, `TestLoadConfigMissingUsesPrivateDefaults` |
| `paos scan` discovers Control Plane artifacts and broken refs. | `TestScanControlPlaneArtifacts`, `TestScanReportsBrokenRefs` |
| `paos scan` is read-only from the user's Git perspective. | `TestRunCLIScanLeavesGitStatusUnchanged` |
| `paos watch --once` reports local Control Plane state without calling LLM or writing files. | `TestRunCLIWatchOnceOnlyReportsControlPlaneState` |
| `paos draft` creates a Runtime Task Draft from a `ready-for-agent` Issue. | `TestCreateDraftRuntimeTaskFromReadyIssue`, `TestRunCLIDraftCreatesTaskWithoutProjectSourcePayload` |
| `paos draft` refuses unready parents before LLM calls. | `TestCreateDraftRuntimeTaskRefusesUnreadyParentBeforeLLMCall` |
| `paos draft` refuses parents outside `.scratch/<feature>` before LLM calls. | `TestCreateDraftRuntimeTaskRefusesParentOutsideScratchBeforeLLMCall` |
| Default LLM Payload excludes project source files. | `TestRunCLIDraftCreatesTaskWithoutProjectSourcePayload` |
| Repair payload includes failed task result text and log refs, not Private Runtime Log contents. | `TestRepairPayloadExcludesPrivateLogContents` |
| LLM output must be strict JSON and schema-valid. | `TestParseDraftResponseRejectsMalformedOutput`, `TestOpenAICompatibleClientParsesStrictStructuredOutput` |
| `paos approve` creates an Approval Record and moves the Runtime Task to `ready`. | `TestApproveRuntimeTaskCreatesRecordAndMarksReady` |
| `paos approve` rejects incomplete execution boundaries. | `TestApproveRuntimeTaskRejectsMissingCommandList` |
| `paos run` refuses tasks without durable Approval Records. | `TestRunRuntimeTaskRefusesWithoutApprovalRecord` |
| `paos run` verifies the Approval Record points to the current Runtime Task. | `TestRunRuntimeTaskRejectsApprovalRecordForDifferentTask` |
| `paos run` rejects execution-boundary drift after approval. | `TestRunRuntimeTaskRejectsBoundaryChangedAfterApproval` |
| `paos run` creates a dedicated Git worktree, executes only approved commands, writes full Private Runtime Logs outside Git, and only links summaries to Control Plane. | `TestRunRuntimeTaskExecutesApprovedCommandAndWritesPrivateLog` |

## Remaining Gaps

- The current watcher is polling-based and covered by `--once`; long-running event-loop behavior is not deeply tested.
- CLI argument parsing is minimal and covered only through representative command paths.
- Dedicated worktree cleanup is not implemented in Runtime v1 and therefore not tested.
- Network intent is recorded and approved, but Runtime v1 does not enforce domain-level network policy by design.

## Future Rule

For any new Runtime behavior, use vertical TDD slices:

```text
RED: one public behavior test
GREEN: minimum implementation
REFACTOR: only after the focused test and full suite pass
```

Do not change a test merely to make it pass. A test may be corrected only when it demonstrably conflicts with the PRD, ADR, issue acceptance criteria, or observable user-facing behavior.
