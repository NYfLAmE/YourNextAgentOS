---
artifact_type: prd
title: Personal Agent OS Runtime v1 controlled execution loop
status: draft
source_refs:
  - ../../CONTEXT.md
  - ../../docs/adr/0002-markdown-git-control-plane.md
  - ../../docs/adr/0006-task-scoped-plan-approved-autonomy.md
  - ../../docs/adr/0009-local-control-plane-events-first.md
  - ../../docs/adr/0010-task-scoped-runtime-execution-safety.md
  - ../../templates/runtime-task.md
  - ../../templates/approval-record.md
confidence: medium
approval_state: draft
risk_level: medium
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# PRD: Personal Agent OS Runtime v1 Controlled Execution Loop

## Problem

Personal Agent OS currently defines the Control Plane, approval policy, templates, and architecture decisions, but it does not yet define the first executable Runtime slice. Without a PRD for the controlled execution loop, implementers could jump directly to Builder automation, arbitrary shell execution, or external connectors before proving the core Runtime boundary.

## Target User

The target user is the local Personal Agent OS owner who wants `paos` to observe approved local Control Plane work, run explicitly approved commands in a bounded Execution Workspace, and record auditable results without taking over full coding autonomy.

## Goals

- Define Runtime v1 as a controlled execution loop, not complete Builder automation.
- Let `paos` watch local Control Plane changes and manually reconcile missed events.
- Let `paos` draft Runtime Tasks for `ready-for-agent` Issues or approved Plans.
- Let the user approve the full execution boundary through CLI-generated or Markdown Approval Records.
- Let `paos` execute approved Command Lists inside task-scoped Execution Workspaces.
- Store full stdout, stderr, command, timing, and exit result in Private Runtime Logs.
- Write workflow results back to the Runtime Task and a short summary link to the parent Issue or Plan.

## Non-Goals

- No Telegram, email, calendar, browser history, or other external connectors.
- No direct mailbox ingestion or external message sending.
- No automatic code repair or Builder autonomy.
- No arbitrary shell beyond the approved Command List.
- No Runtime implementation in this PRD artifact.
- No domain-level firewall or network egress enforcement in v1.

## User Stories

1. As a Personal Agent OS owner, I want a `ready-for-agent` Issue to produce a draft Runtime Task so that execution can be reviewed before it starts.
2. As a reviewer, I want a Runtime Task to show its Execution Workspace, Command List, Env Profile, Network Intent, and log policy so that approval has a precise boundary.
3. As a Runtime operator, I want `paos approve <task>` to create an Approval Record and mark the task ready so that approved work can proceed without repeated command-by-command prompts.
4. As a Runtime operator, I want `paos run <task>` and `paos watch` to execute only approved Command Lists so that commands cannot drift beyond the approved task.
5. As a reviewer, I want failed execution to produce a draft follow-up Runtime Task instead of direct LLM edits so that repair remains auditable.

## Requirements

- Runtime Task files live under `.scratch/<feature>/runtime-tasks/<NN>-<slug>.md` and use `artifact_type: runtime_task`.
- Runtime Task state uses `draft -> ready -> running -> succeeded|failed|blocked|cancelled`.
- `status` and `approval_state` are separate fields; both must permit execution before `paos` runs commands.
- Approval Records live under `.scratch/<feature>/approvals/<id>.md` and use `artifact_type: approval_record`.
- An Approval Record approves the Runtime Task, Execution Workspace, Command List, Env Profile, Network Intent, and Private Runtime Log policy as one boundary.
- Runtime Task execution uses explicit Command Lists, not natural-language execution plans.
- `paos watch` observes local Control Plane changes; `paos scan` manually reconciles startup, missed events, and troubleshooting.
- `paos approve <task>` creates or links an Approval Record and moves an approved task to `ready`.
- `paos run <task>` executes an approved ready task on demand.
- `paos status` reports watcher state, pending tasks, blocked tasks, and recent results.
- Private Runtime Logs stay outside the Git-backed Control Plane and are linked by reference, not copied into reports by default.
- On failure, LLM-assisted repair may create a new `draft` Runtime Task that cites the failed task and log refs, but it must not edit files directly.
- The default private local config path is `~/.personal-agent-os/config.yaml`.
- `paos approve <task>` records the local user by default and may accept an explicit approver value when needed.
- `paos` creates dedicated Git worktrees for Execution Workspaces by default.

## Acceptance Criteria

- [ ] A sample `ready-for-agent` Issue in this repository can be used to draft a Runtime Task under `.scratch/<feature>/runtime-tasks/`.
- [ ] A sample Runtime Task can list safe documentation checks such as `git diff --check` and link to its parent Issue or Plan.
- [ ] A sample Approval Record can approve the Runtime Task's Execution Workspace, Command List, Env Profile, Network Intent, and Private Runtime Log policy.
- [ ] The documented `paos` command surface includes `watch`, `scan`, `approve <task>`, `run <task>`, and `status`.
- [ ] The Runtime Task template distinguishes workflow state from Private Runtime Log refs.
- [ ] The Approval Record template is independent from `approval_state` and records the approved execution boundary.
- [ ] A failed execution path produces a draft follow-up Runtime Task instead of direct LLM file edits.
- [ ] The PRD contains no requirement for Telegram, email, calendar, browser history, or external connector access.

## Evidence

- `CONTEXT.md`: defines Runtime, Control Plane, Runtime Task, Approval Record, Execution Workspace, Command List, Env Profile, Network Intent, and Private Runtime Log.
- `docs/adr/0002-markdown-git-control-plane.md`: establishes Git-backed Markdown as the Control Plane.
- `docs/adr/0006-task-scoped-plan-approved-autonomy.md`: establishes task-scoped autonomy.
- `docs/adr/0009-local-control-plane-events-first.md`: keeps v1 event sources local.
- `docs/adr/0010-task-scoped-runtime-execution-safety.md`: establishes worktree, command, env, network, and log boundaries.

## Risks

- Explicit Command Lists may be too verbose for large tasks; mitigation is LLM draft generation plus one Approval Record per Runtime Task.
- Full unredacted Private Runtime Logs carry privacy risk; mitigation is private local storage outside Git and no default report use.
- Default network access can leak data if paired with a broad Env Profile; mitigation is default empty environment and explicit task-scoped Env Profiles.
- Watcher behavior can miss filesystem events; mitigation is `paos scan` reconciliation.

## Implementation Defaults

- Private local config defaults to `~/.personal-agent-os/config.yaml`.
- Dedicated worktrees default to a private runtime directory configured outside Git.
- `paos approve <task>` records the local OS user by default and can support an explicit approver override.
- Runtime v1 treats network access as allowed by default but records Network Intent in the Runtime Task and Approval Record.
