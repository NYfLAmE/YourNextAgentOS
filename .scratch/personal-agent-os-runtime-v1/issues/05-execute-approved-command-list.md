---
artifact_type: issue
title: execute approved Command List
status: ready-for-human
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0010-task-scoped-runtime-execution-safety.md
  - ../../../docs/adr/0011-runtime-task-execution-request.md
confidence: medium
approval_state: approved
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: execute approved Command List

## Parent

`../PRD.md`

## What To Build

Implement `paos run <task>` for approved Runtime Tasks. It should verify the task and Approval Record, create or use a task-scoped Execution Workspace, execute only the approved Command List, write full output to Private Runtime Logs, and link log references back to the Runtime Task.

## Acceptance Criteria

- [ ] `paos run <task>` refuses tasks that are not `ready` and approved by an Approval Record.
- [ ] Execution uses a dedicated Git worktree by default.
- [ ] Only approved Command List entries run; no new command can be introduced at runtime.
- [ ] Default environment starts empty except required safe process variables and approved Env Profile values.
- [ ] Full stdout, stderr, command, timing, and exit status are written to Private Runtime Logs outside Git.
- [ ] Runtime Task status moves to `running` then `succeeded` or `failed`.
- [ ] Parent Issue or Plan receives only a short summary and log reference, not full private logs.

## Blocked By

- `04-approval-record-flow.md`

## Implementation Notes

This issue may introduce process execution, so keep the first self-test command safe, such as documentation validation in this repository. Do not implement arbitrary shell outside approved Command Lists.

## Test Plan

- Fixture test refusing unapproved Runtime Task.
- Integration test running a harmless command in a temporary Git repository.
- Verify logs are written outside the Git-backed Control Plane.
- Verify `git status --short` in the main repo is not polluted by private logs.

## Risks

- Execution code is high risk because it can change files or leak output if boundaries are wrong.

## Comments

Append discussion and triage notes here.

Implementation note 2026-05-10:

- Implemented `paos run <task>` for tasks with `status: ready`, `approval_state: approved`, and a matching Approval Record.
- Runtime creates a dedicated Git worktree, executes only the approved Command List, and writes full command logs under the private runtime directory.
- Runtime Task and parent Issue/Plan receive short result summaries and log references, not full stdout/stderr contents.
