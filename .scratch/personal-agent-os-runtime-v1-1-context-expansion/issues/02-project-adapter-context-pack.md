---
artifact_type: issue
title: project adapter context pack
status: needs-triage
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../projects/terra-openclaw-setup-backend.md
  - ../../../docs/adr/0015-runtime-v1-1-controlled-context-expansion.md
  - ../../../../TerraOpenclawSetupBackend/docs/ai-collaboration/workflow-rules.md
  - ../../../../TerraOpenclawSetupBackend/docs/agents/usage.md
confidence: medium
approval_state: draft
risk_level: medium
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: project adapter context pack

## Parent

`../PRD.md`

## What To Build

Add deterministic project adapter resolution for Runtime Drafting. For Terra/OpenClaw work, the context pack must include the Personal Agent OS Terra adapter and the required Terra onboarding/collaboration route, while preserving the rule that current files, tests, and command output are the factual source of truth.

## Acceptance Criteria

- [ ] Selects a project adapter from parent path, configured project root, or explicit parent metadata.
- [ ] Includes adapter identity and required reading rules in the LLM Payload.
- [ ] For Terra/OpenClaw, includes `projects/terra-openclaw-setup-backend.md` and `$terra-onboarding` route output or equivalent required file list.
- [ ] Does not touch or modify the Terra working tree while drafting.
- [ ] Does not treat adapter output as verified code facts.
- [ ] Records adapter context in the Runtime Task Draft's source/context section.
- [ ] Adds behavior tests for a Terra parent and for an unknown project fallback.

## Implementation Notes

The current Terra repository may have unrelated dirty files. Tests should use temporary fixtures and must not depend on the real Terra worktree state.

## Test Plan

- RED: Terra-like parent resolves Terra adapter context.
- RED: unknown parent uses no project adapter and still drafts safely.
- GREEN: implement minimal adapter registry/resolver.
- REFACTOR: keep adapter loading separate from `source_refs` file inclusion.

## Risks

- A stale adapter can mislead drafts if treated as fact. The payload should state that adapter context is routing guidance and must be verified against current files when used for implementation.

## Comments

Append discussion and triage notes here.
