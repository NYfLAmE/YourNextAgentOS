---
artifact_type: prd
title: Personal Agent OS Runtime v1.1 controlled context expansion
status: draft
source_refs:
  - ../../CONTEXT.md
  - ../../README.md
  - ../../workflows/engineering-delivery.md
  - ../../system/risk-and-hitl-policy.md
  - ../../docs/adr/0010-task-scoped-runtime-execution-safety.md
  - ../../docs/adr/0014-llm-drafting-in-runtime-v1.md
  - ../../docs/adr/0015-runtime-v1-1-controlled-context-expansion.md
  - ../../docs/runtime-v1-self-test.md
  - ../../docs/runtime-v1-tdd-hardening.md
  - ../../templates/runtime-task.md
  - ../../templates/approval-record.md
  - ../../projects/terra-openclaw-setup-backend.md
  - ../../../TerraOpenclawSetupBackend/docs/ai-collaboration/workflow-rules.md
  - ../../../TerraOpenclawSetupBackend/docs/agents/usage.md
confidence: medium
approval_state: draft
risk_level: medium
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# PRD: Personal Agent OS Runtime v1.1 Controlled Context Expansion

## Problem

Runtime v1 can discover `ready-for-agent` Issues, create strict Runtime Task Drafts, approve tasks with durable Approval Records, run approved Command Lists in dedicated worktrees, and write Private Runtime Logs outside the Git-backed Control Plane. The current draft payload is intentionally small: it includes parent Control Plane text, domain context, selected ADRs, and the Runtime Task template, while excluding project source files and Private Runtime Log contents.

That boundary is safe, but it is not enough for high-quality implementation tasks. A `ready-for-agent` Issue may cite `source_refs`, project-specific workflow rules, TDD expectations, and code or docs that a fresh Builder must read before implementation. Runtime v1.1 needs a controlled way to bring those inputs into LLM Drafting without turning LLM Drafting into unattended Builder automation.

## Target User

The target user is the local Personal Agent OS owner who wants `paos` to produce better Runtime Task Drafts from specified local evidence, while preserving HITL approval for execution and preserving project-specific collaboration rules such as Terra/OpenClaw onboarding.

## Goals

- Resolve explicit `source_refs` from parent artifacts into a bounded context pack.
- Select project adapter context when the parent artifact belongs to a known project or repository.
- Make Runtime Task Drafts TDD-aware for implementation work.
- Decide watcher drafting policy without weakening the current report-only default.
- Preserve Approval Record requirements before any command execution or code/config/script/runtime-state/behavior change.

## Non-Goals

- No unattended Builder automation.
- No automatic approve or run from watcher events.
- No default project-wide source tree ingestion.
- No Private Runtime Log contents in LLM Payloads by default.
- No credentials, private config, environment secrets, cookies, tokens, or API keys in Control Plane artifacts.
- No external connectors such as email, calendar, browser history, chat, GitHub, GitLab, Jira, or Linear.
- No domain-level network firewall enforcement in this PRD.

## User Stories

1. As a Runtime operator, I want `paos draft <parent>` to read the parent artifact's explicit `source_refs`, so that the draft can cite the same evidence a human reviewer expects.
2. As a reviewer, I want the draft to show which context files were included and excluded, so that I can audit the LLM Payload boundary.
3. As a Terra/OpenClaw operator, I want the Terra adapter to route the draft through `$terra-onboarding` and mandatory collaboration docs, so that generated tasks do not ignore project rules.
4. As a Builder, I want implementation drafts to include RED, GREEN, and REFACTOR/validation steps, so that TDD is part of the executable task boundary.
5. As a Runtime operator, I want `watch` to remain safe by default, so that local observation does not silently call the LLM, approve tasks, or run commands.
6. As a system owner, I want all code-changing or behavior-changing execution to remain gated by Approval Records, so that better drafting does not become global autonomy.

## Requirements

- `paos draft <parent>` must parse `source_refs` from frontmatter only; body links are not authorization to read extra files.
- Source references may be relative or absolute. Relative paths resolve from the parent artifact file directory.
- Absolute paths may point outside the current repo only when explicitly listed in `source_refs`.
- The resolver must reject Private Runtime Log paths, PAOS private config paths, `.git` internals, credential-shaped files, binary/non-UTF-8 files, and unapproved external URLs by default.
- Plain `source_refs` are not credential-reading authorization; credential-shaped files require a future high-risk ADR before any support is added.
- Included file content is capped at 64KB per file. Runtime v1.1 has no global Context Pack total-size limit.
- Runtime Task Drafts must persist Context Pack metadata only; they must not copy included file contents into the Git-backed Control Plane.
- Each included context item must record path, byte size or truncation status, reason, and source field.
- Each excluded context item must record path or ref, exclusion reason, and whether user approval could change the decision.
- Project adapter selection must be deterministic from the parent path, configured project root, or explicit adapter metadata.
- The Terra/OpenClaw adapter must include `projects/terra-openclaw-setup-backend.md` and route to `$terra-onboarding` or an equivalent context-pack helper before drawing Terra-specific conclusions.
- Adapter output is advisory context and reading guidance; it must not override current source files, tests, command output, or explicit user instructions.
- Runtime Task Drafts for implementation work must include a TDD plan with RED, GREEN, and REFACTOR/validation sections.
- Command Lists must remain explicit Command Templates; they must not contain open-ended natural-language shell instructions.
- Code/config/script/runtime-state/behavior-changing commands are high risk and require task-scoped Approval Records before execution.
- `paos watch` must remain report-only by default.
- Any watcher-assisted drafting mode must be explicit opt-in, create draft Runtime Tasks only, avoid duplicate drafts for the same parent, and never approve or run.

## Acceptance Criteria

- [ ] Given a `ready-for-agent` Issue with frontmatter `source_refs`, `paos draft <parent>` includes an auditable context pack in the LLM Payload and resulting Runtime Task Draft.
- [ ] Given a relative `source_refs` entry, `paos draft <parent>` resolves it from the parent artifact directory.
- [ ] Given an explicit absolute `source_refs` entry outside the repo, `paos draft <parent>` may include it if it is text and not sensitive.
- [ ] Given a Private Runtime Log, PAOS private config, `.git`, credential-shaped, binary, or URL reference, `paos draft <parent>` excludes it with a visible reason before calling the LLM.
- [ ] Given a file larger than 64KB, `paos draft <parent>` truncates the LLM Payload content and records `truncated=true`.
- [ ] The Runtime Task Draft `## Context Pack` section records full absolute paths and metadata only, not included file contents.
- [ ] Given a Terra/OpenClaw parent artifact, project adapter resolution adds Terra onboarding and collaboration-rule context without touching the Terra working tree.
- [ ] Generated implementation Runtime Task Drafts include RED, GREEN, and REFACTOR/validation intent.
- [ ] Existing v1 guarantees remain true: strict LLM output, default exclusion of Private Runtime Log contents, no default project-wide source ingestion, and no execution before Approval Record.
- [ ] `paos watch --once` remains report-only and continues not to call the LLM or write files.
- [ ] If an explicit watcher-assisted drafting mode is implemented, it creates draft artifacts only and leaves approval/run to separate user actions.

## Evidence

- `CONTEXT.md` defines Runtime Task Drafts as reviewable drafts, LLM Payloads as bounded provider input, and Approval Records as durable permissions.
- `README.md` documents the current `paos` command surface and states `watch` does not call LLM, approve, or run by itself.
- `docs/adr/0014-llm-drafting-in-runtime-v1.md` says the default LLM Payload excludes Private Runtime Logs and project source files unless a later approved design expands that boundary.
- `docs/runtime-v1-self-test.md` records the current self-test boundary and parent Issue transition after run results.
- `docs/runtime-v1-tdd-hardening.md` records current tests, remaining gaps, and the required RED/GREEN/REFACTOR rule for future Runtime behavior.
- `projects/terra-openclaw-setup-backend.md` and Terra collaboration docs require fact-based reading, dirty-tree hygiene, docs-sync review, and approval before high-risk changes.

## Risks

- Expanding context can leak private data if path resolution is too broad; mitigation is explicit frontmatter-only references, exclusion records, 64KB per-file truncation, and tests for blocked sensitive paths.
- Adapter output can become stale; mitigation is to treat adapters as routing context only and re-read current files during each draft.
- TDD wording can become decorative; mitigation is schema-level fields and tests that reject implementation drafts without RED/GREEN/REFACTOR intent.
- Watcher-assisted drafting can surprise the user; mitigation is report-only default and explicit opt-in if implemented.
- Runtime Task Drafts can overstate execution authority; mitigation is to keep Approval Records mandatory and visible.

## Open Questions

- Should watcher-assisted drafting be a v1.1 implementation requirement, or should v1.1 only preserve `watch` as report-only and improve explicit `paos draft <parent>`?
- What exact adapter selection mechanism should be used first: path prefix, repo root config, or explicit parent frontmatter?
- No global Context Pack total-size limit is set in v1.1; revisit this if payload size becomes a practical provider limit.
