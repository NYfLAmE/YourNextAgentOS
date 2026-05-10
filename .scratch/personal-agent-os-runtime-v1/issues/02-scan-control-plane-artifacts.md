---
artifact_type: issue
title: scan Control Plane artifacts
status: ready-for-human
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0002-markdown-git-control-plane.md
  - ../../../docs/adr/0013-watcher-and-scan-trigger-model.md
confidence: medium
approval_state: approved
risk_level: medium
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: scan Control Plane artifacts

## Parent

`../PRD.md`

## What To Build

Implement read-only `paos scan` for local Control Plane artifacts. It should discover PRDs, Issues, Runtime Tasks, and Approval Records under `.scratch/`, parse their frontmatter, and report draft, ready, running, blocked, failed, and succeeded work without modifying files.

## Acceptance Criteria

- [ ] `paos scan` reads `.scratch/**.md` and identifies `artifact_type`.
- [ ] It reports `ready-for-agent` Issues or approved Plans that can be passed to `paos draft <parent>`.
- [ ] It reports Runtime Tasks by status and approval state.
- [ ] It reports missing or broken parent refs and approval refs as warnings.
- [ ] It is read-only: running `paos scan` leaves `git status --short` unchanged.

## Blocked By

- `01-paos-cli-skeleton-and-config.md`

## Implementation Notes

Use structured frontmatter parsing instead of ad hoc string matching. `scan` must not call the LLM and must not create Runtime Task Drafts.

## Test Plan

- Fixture tests for PRD, Issue, Runtime Task, and Approval Record files.
- Test malformed frontmatter reporting.
- Run `paos scan` against the Personal Agent OS repo and verify no file changes.

## Risks

- If scan writes files, it will blur the boundary between reconciliation and execution.

## Comments

Append discussion and triage notes here.

Implementation note 2026-05-10:

- Implemented read-only `.scratch/**.md` scanning with structured YAML frontmatter parsing.
- Scan reports PRDs, Issues, Runtime Tasks, Approval Records, draft opportunities, Runtime Task statuses, and broken parent or approval refs.
- `paos scan` does not call LLM providers and does not write Control Plane files.
