---
artifact_type: issue
title: LLM draft Runtime Task
status: ready-for-human
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0005-strict-llm-output-contract.md
  - ../../../docs/adr/0011-runtime-task-execution-request.md
  - ../../../docs/adr/0014-llm-drafting-in-runtime-v1.md
  - ../../../templates/runtime-task.md
confidence: medium
approval_state: approved
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: LLM draft Runtime Task

## Parent

`../PRD.md`

## What To Build

Implement `paos draft <parent>` so Runtime v1 can call a configured LLM and create a draft Runtime Task from a `ready-for-agent` Issue or approved Plan. The LLM must return strict structured output, and `paos` must render validated output into `templates/runtime-task.md` shape.

## Acceptance Criteria

- [ ] `paos draft <parent>` builds an LLM Payload from the parent artifact and relevant Control Plane summaries.
- [ ] Default payload excludes Private Runtime Logs and project source files.
- [ ] The provider call uses private OpenAI-compatible config and reads secrets only through `api_key_env`.
- [ ] The LLM output is schema-constrained; malformed output fails without heuristic repair.
- [ ] A valid response creates `.scratch/<feature>/runtime-tasks/<NN>-<slug>.md` with `status: draft` and `approval_state: draft`.
- [ ] Draft creation never executes commands and never modifies project source files.

## Blocked By

- `01-paos-cli-skeleton-and-config.md`
- `02-scan-control-plane-artifacts.md`

## Implementation Notes

This is LLM Drafting only, not Builder automation. The Command List can be model-drafted, but it is not executable until an Approval Record approves it.

## Test Plan

- Unit test payload construction.
- Mock provider tests for valid structured output.
- Mock provider tests for malformed output rejection.
- Fixture test that generated Markdown follows `templates/runtime-task.md`.

## Risks

- Sending too much context to the provider would violate the LLM Payload boundary.
- Accepting free-form output would violate ADR-0005.

## Comments

Append discussion and triage notes here.

Implementation note 2026-05-10:

- Implemented `paos draft <parent>` with bounded LLM Payload construction from Control Plane text, ADR summaries, and the Runtime Task template.
- Implemented OpenAI-compatible provider calls through private config and `api_key_env`.
- Implemented strict JSON validation and Markdown rendering to `.scratch/<feature>/runtime-tasks/<NN>-<slug>.md` with `status: draft` and `approval_state: draft`.
