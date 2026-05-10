---
artifact_type: issue
title: LLM repair draft from failure
status: needs-triage
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0005-strict-llm-output-contract.md
  - ../../../docs/adr/0014-llm-drafting-in-runtime-v1.md
confidence: medium
approval_state: draft
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: LLM repair draft from failure

## Parent

`../PRD.md`

## What To Build

Extend `paos draft` so it can create a follow-up Runtime Task Draft from a failed Runtime Task. The LLM should receive Control Plane result text and log references by default, not full Private Runtime Log contents or project source files.

## Acceptance Criteria

- [ ] `paos draft <failed-task>` can create a new `status: draft` Runtime Task.
- [ ] The new draft cites the failed Runtime Task and relevant log references.
- [ ] Default LLM Payload excludes full Private Runtime Logs and project source files.
- [ ] The LLM output remains schema-constrained and is rejected if malformed.
- [ ] The repair draft does not edit files, execute commands, approve itself, or retry automatically.

## Blocked By

- `03-llm-draft-runtime-task.md`
- `05-execute-approved-command-list.md`

## Implementation Notes

This preserves the v1 boundary: LLM can propose the next Runtime Task, but human approval remains required before execution.

## Test Plan

- Fixture test creating a repair draft from a failed Runtime Task.
- Mock provider test ensuring payload contains result summary and refs but not full private log content.
- Test malformed repair output rejection.

## Risks

- Sending private logs to the provider by default would violate the LLM Payload boundary.

## Comments

Append discussion and triage notes here.
