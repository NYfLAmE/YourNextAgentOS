---
artifact_type: issue
title: self-test controlled execution flow
status: ready-for-human
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../templates/runtime-task.md
  - ../../../templates/approval-record.md
confidence: medium
approval_state: approved
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: self-test controlled execution flow

## Parent

`../PRD.md`

## What To Build

Create the Runtime v1 self-test scenario inside the Personal Agent OS repository. The self-test should verify the full controlled execution loop: draft, approve, run, log, result feedback, and failure repair draft boundaries.

## Acceptance Criteria

- [ ] A sample `ready-for-agent` Issue can be used by `paos draft <parent>` to create a Runtime Task Draft.
- [ ] A sample Approval Record approves the Runtime Task's execution boundary.
- [ ] `paos run <task>` executes a safe documentation validation Command List such as `git diff --check`.
- [ ] The Runtime Task records status and Private Runtime Log refs without pasting full logs into the Control Plane.
- [ ] A forced failure can produce a follow-up draft Runtime Task without direct file edits.
- [ ] The self-test demonstrates that Telegram, email, calendar, browser history, and project source payload expansion are not required.

## Blocked By

- `01-paos-cli-skeleton-and-config.md`
- `02-scan-control-plane-artifacts.md`
- `03-llm-draft-runtime-task.md`
- `04-approval-record-flow.md`
- `05-execute-approved-command-list.md`
- `06-llm-repair-draft-from-failure.md`
- `07-watch-and-status-loop.md`

## Implementation Notes

Use `personal-agent-os` itself for the first acceptance scenario because it minimizes project-specific risk and keeps evidence local.

## Test Plan

- Run the documented self-test from a clean working tree.
- Verify `git status --short` excludes private runtime logs.
- Verify all generated Control Plane artifacts cite source references.

## Risks

- A self-test that depends on real external connectors would exceed Runtime v1 scope.

## Comments

Append discussion and triage notes here.

Implementation note 2026-05-10:

- Added automated self-tests covering config, scan, LLM drafting, approval, run, private log boundaries, and repair payload construction.
- Added `docs/runtime-v1-self-test.md` with the local test and manual smoke-check boundary.
- The self-test uses temporary directories, a mock LLM provider, and a temporary Git repository; it does not require external connectors or a real API key.

TDD hardening note 2026-05-10:

- Added `docs/runtime-v1-tdd-hardening.md` to record the corrective RED/GREEN pass and behavior coverage matrix.
- Added public CLI behavior tests for read-only `scan`, report-only `watch --once`, and source-excluding `draft`.
- Fixed two tested boundary gaps: `run` now rejects execution-boundary drift after approval, and `draft` now rejects parents outside `.scratch/<feature>` before building LLM payloads.

Acceptance refinement note 2026-05-10:

- `paos run` now moves the parent Issue from `ready-for-agent` to `ready-for-human` after writing Runtime result feedback, preventing repeated draft opportunities for the same handled Issue.
- `paos approve` now replaces pending approval wording in the Runtime Task and keeps Markdown headings separated by a blank line.
