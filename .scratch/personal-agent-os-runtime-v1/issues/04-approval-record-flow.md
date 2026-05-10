---
artifact_type: issue
title: Approval Record flow
status: ready-for-human
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0006-task-scoped-plan-approved-autonomy.md
  - ../../../docs/adr/0010-task-scoped-runtime-execution-safety.md
  - ../../../templates/approval-record.md
confidence: medium
approval_state: approved
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: Approval Record flow

## Parent

`../PRD.md`

## What To Build

Implement `paos approve <task>` so a human can approve a Runtime Task's execution boundary. The command should create an Approval Record, link it from the Runtime Task, and move the task to `ready` only when the approved boundary is complete.

## Acceptance Criteria

- [ ] `paos approve <task>` creates `.scratch/<feature>/approvals/<id>.md`.
- [ ] The Approval Record includes Runtime Task, Execution Workspace, Command List, Env Profile, Network Intent, and Private Runtime Log policy.
- [ ] The command records the local OS user by default and supports an explicit approver override.
- [ ] The Runtime Task gains an `approval_refs` entry and moves to `status: ready` / `approval_state: approved`.
- [ ] Approval fails if the Runtime Task has no explicit Command List or workspace.

## Blocked By

- `02-scan-control-plane-artifacts.md`
- `03-llm-draft-runtime-task.md`

## Implementation Notes

Approval is durable and local. A transient CLI confirmation is not enough unless it writes the Approval Record.

## Test Plan

- Fixture test approving a complete Runtime Task.
- Test refusal for missing Command List.
- Test refusal for missing Execution Workspace.
- Verify generated Approval Record follows `templates/approval-record.md`.

## Risks

- Treating `approval_state: approved` alone as sufficient would bypass the Approval Record model.

## Comments

Append discussion and triage notes here.

Implementation note 2026-05-10:

- Implemented `paos approve <task>` with explicit approver override and local-user default.
- Approval writes `.scratch/<feature>/approvals/<id>.md`, records the approved execution boundary, and links it from the Runtime Task.
- Approval refuses Runtime Tasks without a complete Execution Workspace or Command List.
