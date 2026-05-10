---
artifact_type: issue
title: watch and status loop
status: ready-for-human
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0009-local-control-plane-events-first.md
  - ../../../docs/adr/0013-watcher-and-scan-trigger-model.md
confidence: medium
approval_state: approved
risk_level: medium
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: watch and status loop

## Parent

`../PRD.md`

## What To Build

Implement `paos watch` and complete `paos status` for Runtime v1. The watcher should observe local Control Plane changes, surface draft opportunities, ready tasks, running tasks, blocked tasks, and recent results, while relying on `paos scan` for deterministic reconciliation.

## Acceptance Criteria

- [ ] `paos watch` observes approved local Control Plane paths only.
- [ ] Watcher startup runs the same reconciliation logic as `paos scan`.
- [ ] `paos status` reports pending draft opportunities, draft tasks, ready tasks, running tasks, blocked or failed tasks, and recent results.
- [ ] Watcher does not call LLM, approve tasks, or run commands without explicit user action or already-approved Runtime Task transitions.
- [ ] Missed events can be recovered by `paos scan`.

## Blocked By

- `02-scan-control-plane-artifacts.md`
- `03-llm-draft-runtime-task.md`
- `04-approval-record-flow.md`
- `05-execute-approved-command-list.md`

## Implementation Notes

Keep v1 event sources local. Telegram, email, calendar, browser history, and other external connectors remain out of scope.

## Test Plan

- Unit test status aggregation.
- Integration test watcher noticing a new draft Runtime Task.
- Verify watcher does not write files when only reporting status.

## Risks

- A watcher that silently performs LLM calls or command execution would blur HITL boundaries.

## Comments

Append discussion and triage notes here.

Implementation note 2026-05-10:

- Implemented `paos status` aggregation for draft opportunities, draft tasks, ready tasks, running tasks, blocked/failed tasks, and recent results.
- Implemented `paos watch` as a local polling watcher with `--once` and `--interval`; watcher startup uses scan reconciliation.
- Watcher only reports local Control Plane state and does not call LLM providers, approve tasks, or run commands by itself.
