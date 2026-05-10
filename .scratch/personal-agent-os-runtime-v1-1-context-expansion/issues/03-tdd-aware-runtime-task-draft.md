---
artifact_type: issue
title: TDD aware Runtime Task Draft schema
status: needs-triage
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../docs/runtime-v1-tdd-hardening.md
  - ../../../templates/runtime-task.md
  - ../../../docs/adr/0005-strict-llm-output-contract.md
  - ../../../docs/adr/0015-runtime-v1-1-controlled-context-expansion.md
confidence: medium
approval_state: draft
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: TDD aware Runtime Task Draft schema

## Parent

`../PRD.md`

## What To Build

Extend strict LLM Drafting so implementation Runtime Task Drafts include a structured TDD plan. Drafts should distinguish RED, GREEN, REFACTOR, and validation intent and should keep Command Lists as explicit Command Templates rather than natural-language shell instructions.

## Acceptance Criteria

- [ ] Extends the strict draft response schema with TDD plan fields for implementation work.
- [ ] Renders a TDD plan section into Runtime Task Markdown.
- [ ] Rejects implementation drafts that omit RED/GREEN/REFACTOR intent.
- [ ] Keeps malformed or unknown JSON fields rejected.
- [ ] Requires Command List entries to remain concrete command templates.
- [ ] Distinguishes test/validation commands from any high-risk implementation command.
- [ ] Documents that TDD is an execution rule for Builder work, not optional guidance.

## Implementation Notes

This issue changes Runtime Task Draft semantics, so docs sync is required for `templates/runtime-task.md`, `docs/runtime-v1-tdd-hardening.md`, or another durable runtime document.

## Test Plan

- RED: schema-valid implementation draft without TDD plan fails.
- RED: schema-valid documentation-only draft behavior is explicitly accepted or rejected according to the final PRD decision.
- RED: unknown JSON fields remain rejected.
- GREEN: add the minimum schema, renderer, and validation.
- REFACTOR: keep draft validation readable and covered by public behavior tests.

## Risks

- If the schema only adds prose fields, TDD can become decorative. Tests must assert behavior, not just text presence.

## Comments

Append discussion and triage notes here.
