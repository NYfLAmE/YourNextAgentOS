---
artifact_type: issue
title: watch draft policy
status: needs-triage
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../README.md
  - ../../../docs/adr/0013-watcher-and-scan-trigger-model.md
  - ../../../docs/adr/0015-runtime-v1-1-controlled-context-expansion.md
  - ../../../docs/runtime-v1-tdd-hardening.md
confidence: medium
approval_state: draft
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: watch draft policy

## Parent

`../PRD.md`

## What To Build

Decide and implement the v1.1 watcher drafting policy. The safe default is unchanged: `paos watch` reports Control Plane state and does not call the LLM, approve tasks, or run commands. If watcher-assisted drafting is added, it must be explicit opt-in and draft-only.

## Acceptance Criteria

- [ ] Preserves `paos watch` default report-only behavior.
- [ ] Keeps `paos watch --once` from calling the LLM or writing files.
- [ ] If opt-in drafting is implemented, the CLI flag or command name is explicit.
- [ ] Opt-in drafting creates Runtime Task Drafts only.
- [ ] Opt-in drafting does not approve, run, retry, or modify project source files.
- [ ] Avoids duplicate drafts for the same parent while an existing draft/ready/running task is linked.
- [ ] Documents the policy in README or Runtime docs.

## Implementation Notes

This issue is a policy boundary. Do not implement implicit background LLM calls as a side effect of the existing watcher loop.

## Test Plan

- RED: existing `watch --once` report-only behavior remains protected.
- RED: opt-in mode, if selected, creates a draft without approval/run.
- RED: duplicate draft opportunity is skipped when a linked task already exists.
- GREEN: implement the minimum policy and CLI behavior approved by the user.

## Risks

- Silent LLM calls from a watcher would change the autonomy and data-export boundary. Keep the default conservative.

## Comments

Append discussion and triage notes here.
