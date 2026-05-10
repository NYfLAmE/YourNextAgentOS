---
artifact_type: issue
title: Builder boundary ADR and approval contract
status: needs-triage
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../system/risk-and-hitl-policy.md
  - ../../../workflows/engineering-delivery.md
  - ../../../docs/adr/0006-task-scoped-plan-approved-autonomy.md
  - ../../../docs/adr/0010-task-scoped-runtime-execution-safety.md
  - ../../../docs/adr/0015-runtime-v1-1-controlled-context-expansion.md
confidence: medium
approval_state: draft
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: Builder boundary ADR and approval contract

## Parent

`../PRD.md`

## What To Build

Codify the boundary between improved Runtime Drafting and Builder automation before any code-modifying Runtime capability is added. Runtime v1.1 may draft TDD-aware execution requests, but code/config/script/runtime-state/behavior changes must remain gated by Approval Records that approve concrete commands, workspace, environment, network intent, and log policy.

## Acceptance Criteria

- [ ] Confirms whether ADR-0015 is sufficient or whether a follow-up ADR is needed before Builder automation.
- [ ] States that Runtime v1.1 does not grant unattended Builder autonomy.
- [ ] Defines what counts as a code/config/script/runtime-state/behavior-changing command.
- [ ] Requires Approval Record coverage for any such command.
- [ ] Requires TDD RED/GREEN/REFACTOR evidence for implementation work.
- [ ] Documents stop conditions for scope drift, unexpected dirty files, credential needs, or failing tests that reveal a different root cause.
- [ ] Adds tests or docs checks only after the boundary is approved.

## Implementation Notes

This is intentionally a HITL slice. It should be resolved before implementing any feature that lets `paos run` perform Builder-like code changes beyond already approved exact Command Lists.

## Test Plan

- Review ADR and PRD consistency.
- Validate Markdown formatting with `git diff --check`.
- If templates change, add focused tests around approval wording and generated Runtime Task content.

## Risks

- Without this boundary, better context expansion can be mistaken for approval to implement. Keep drafting, approval, and execution as separate states.

## Comments

Append discussion and triage notes here.
