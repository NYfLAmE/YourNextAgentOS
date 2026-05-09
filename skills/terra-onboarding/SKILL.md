---
name: terra-onboarding
description: Bootstrap factual onboarding and task execution for the Terra/OpenClaw workspace by reading required collaboration rules, project docs, and task-specific sources before analysis or edits. Use when working on TerraOpenclawSetupBackend, Terra/OpenClaw packaging, provider/model config, Control UI, restore/reset, logs, or when the user says terra-onboarding, 项目上手, 仓库概况, 工作规范, or wants to stop repeating long onboarding prompts.
---

# Terra Onboarding

## Purpose

Use this skill as the compact replacement for long Terra onboarding prompts. It is a bootstrap router and guardrail, not a fact boundary: current repo files, command output, tests, and explicit user instructions win.

## Quick Start

1. Default repo: `/home/ZykLyj/yjdev/TerraOpenclawSetupBackend`.
2. Run the helper to list the current context pack:

```bash
/home/ZykLyj/.agents/skills/terra-onboarding/scripts/context-pack.sh "<user task summary>"
```

Use `--discover` for unfamiliar topics or when you suspect new docs were added:

```bash
/home/ZykLyj/.agents/skills/terra-onboarding/scripts/context-pack.sh --discover "<user task summary>"
```

3. Read every required file the helper lists as `[required]`.
4. Read `[linked]` candidates from project entry docs when they look relevant.
5. Read task-specific files it lists as `[route]`.
6. Continue following links, code, tests, scripts, ADRs, and sibling repos discovered from those files. The helper never limits the fact surface.
7. Before conclusions, separate verified facts, assumptions, risks, and open questions.
8. If the task is clear and low risk, proceed directly. If edits or risky operations are needed, follow the approval rules below.

## Required Terra Context

Always read these current files before Terra conclusions or work:

- `AGENTS.md`
- `docs/ai-collaboration/*.md` all files, not only README
- `docs/AI-ONBOARDING.md`
- `docs/INDEX.md`
- `docs/agents/usage.md`
- `docs/agents/domain.md`

When facts conflict, use this order: current user instruction, current code/command output, current repo docs, older memory or summaries.

## Task Routing

- Fuzzy requirement: use `grill-with-docs` after onboarding; ask only questions that change scope, behavior, success criteria, or risk.
- Bug, incident, failing test, or performance issue: use `diagnose`; reproduce or build a read-only evidence loop before root-cause claims.
- Clear implementation issue: use `tdd`; propose interface, tests, risks, and acceptance before editing unless the user explicitly requested a small direct edit.
- Old code understanding: use `zoom-out`; map modules, callers, dependencies, and relevant docs.
- Architecture review or refactor opportunity: use `improve-codebase-architecture`; default to read-only findings first.
- PRD or issue work: use `to-prd`, `to-issues`, or `triage`; this repo uses local markdown under `.scratch/`, not GitHub/GitLab by default.
- Do not rerun `setup-matt-pocock-skills` unless `AGENTS.md` or `docs/agents/*` is missing, stale, or the issue tracker/triage/domain-doc configuration changed.

## Common Source Routes

- Provider/model config: read `docs/modelconfig/implementation/claude/00-README.md` and routed files, plus relevant `model/`, `service/`, `handler/`, Swagger, ADR, and tests.
- Snapshot restore/reset: read `docs/restoreFromSyncToAsync/initial_plan.md`, `docs/troubleshooting.md`, `docs/ai-context.md`, `service/snapshot.go`, `handler/snapshot.go`, and `model/snapshot.go`.
- Packaging/install/nginx/migration: inspect `../terraclaw_worktrees/accumulateWithoutAppAndDirChange/`, especially `docs/ci-handoff.md`, `build_root/usr/local/openclaw/scripts/install.sh`, nginx templates, and migration scripts.
- OpenClaw upstream or Control UI behavior: inspect `../openclaw/`, starting with `.ai-context.md`, relevant `INDEX.md`, gateway docs, and source files.
- TAI backend comparison: inspect `../tai-backend/` only when response format, AI backend, Eino/RAG, or model-management comparison is in scope.
- Logs/observability: read `docs/logging-observability/README.md`, `scripts/logs/README.md`, and the matching packaging log tooling when the task crosses packaging boundaries.

## Discovery And Self-Improvement

- Treat `[route]` as a starting hypothesis. If project docs or code reveal a better source, follow the discovered source and cite it.
- If `--discover` shows a stable, recurring doc route that the helper missed, update this skill or helper after the current task is safe.
- Low-risk improvements are allowed when they only clarify wording, add route candidates, or improve discoverability.
- Stop for approval before changing data-source permissions, HITL thresholds, execution autonomy, credential policy, commit/push policy, or any rule that increases side effects.

## Execution Rules

- Default to Chinese prose; keep commands, paths, fields, and identifiers in English.
- Use evidence: cite files, code, tests, command output, or explicit user statements.
- Inspect `git status` before edits in any touched repo.
- Do not touch unrelated dirty files.
- For code, config, script, runtime-state, or behavior-semantic changes, first state intended scope, reason, risks, and validation, then wait for user approval unless the user explicitly asked you to implement that exact change.
- Documentation changes are allowed when the user explicitly asks to write/update docs or preserve a conclusion.
- Every code/config/script/behavior change needs docs-sync review; if no doc update is needed, explain why.
- Never persist credentials, tokens, cookies, private keys, or API keys.

## Completion Checklist

- State the files changed, or say no files were changed.
- Report validation commands and results, or why validation was blocked.
- Report docs-sync outcome.
- For committed work, stage only current-task files and use `type(scope): summary` plus a useful body.
- Push only when remote, credentials, and proxy handling are approved.
