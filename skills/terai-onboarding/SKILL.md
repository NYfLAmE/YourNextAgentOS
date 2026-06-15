---
name: terai-onboarding
description: Bootstrap factual onboarding and task execution for the Terai product and tafs technical base. Use when working on Terai, tafs/Terai architecture, tos-agentd, Terai requirements, Terai beta planning, terai_ye demo comparison, or when user says terai-onboarding, Terai 项目上手, 项目上下文, or wants a fresh agent/GPT to answer or implement Terai-related work.
---

# Terai Onboarding

## Purpose

Use this skill as the compact replacement for long Terai onboarding prompts. It is a bootstrap router and guardrail, not a fact boundary: current repo files, command output, tests, latest meeting records, and explicit user instructions win.

Terai is the product/project name. `tafs` is the high-confidence technical base that will evolve toward the formal framework. `terai_ye` is a demo/reference only; do not treat its Python shim or UI choices as the formal architecture unless current Terai facts or source verification explicitly say so.

## Quick Start

1. Default workspace: `/home/ZykLyj/yjdev`.
2. Run the helper to list the current context pack:

```bash
/home/ZykLyj/.agents/skills/terai-onboarding/scripts/context-pack.sh "<user task summary>"
```

3. Read every `[required]` file.
4. Read `[latest-meeting]` records when the task touches product direction, scope, planning, or decisions.
5. Read `[current]` facts and analysis before older summaries.
6. Read `[source]` and `[route]` files that match the task.
7. Continue following links, code, tests, scripts, sidebars, and sibling repos discovered from those files. The helper never limits the fact surface.
8. Before conclusions, separate `Fact`, `Assumption`, `Decision`, `Risk`, and `Open Question`.

## Fact Priority

When facts conflict, use this order:

1. Current user instruction.
2. Current `tafs` source, command output, tests, and deployed `tos-agentd` behavior.
3. Latest Terai meeting records and `tafs_sidebar/11-terai-current-facts.md`.
4. `tafs_sidebar` source analysis.
5. `terai_ye` source and `terai_ye_sidebar` analysis as demo/reference.
6. Older meeting analysis, memory, or chat context.

Do not infer formal backend architecture from `terai_ye`. Use it for UI/product-demo ideas, packaging clues, API-shape comparison, and migration input only.

## Task Routing

- Fuzzy requirement: use `grill-with-docs` after onboarding; ask only questions that change scope, behavior, success criteria, or risk.
- Old code understanding or source tutoring: use `tafs-mentor` after onboarding. Keep `tafs-mentor` focused on code explanation and learning notes.
- Bug, incident, failing test, or performance issue: use `diagnose`; reproduce or build a read-only evidence loop before root-cause claims.
- Clear implementation issue: use `tdd`; propose interface, tests, risks, and acceptance before editing unless the user explicitly requested a small direct edit.
- Architecture review or refactor opportunity: use `improve-codebase-architecture`; default to read-only findings first.
- PRD or issue work: use `to-prd`, `to-issues`, or `triage`; use local Markdown unless the user explicitly requests a remote tracker.

## Common Source Routes

- Project direction/current facts: `tafs_sidebar/10-terai-onboarding-workflow.md`, `tafs_sidebar/11-terai-current-facts.md`, latest `tafs_sidebar/meeting_log/*_Terai.txt`.
- tafs architecture: `tafs_sidebar/INDEX.md`, `tafs_sidebar/02-architecture-map.md`, `tafs/internal/httpapi/router.go`, `tafs/internal/worker/`, `tafs/internal/agent/`.
- Chat/agent flow: `tafs_sidebar/09-chat-flow-mainline.md`, `tafs_sidebar/03-module-notes/worker-agent-tools.md`.
- Plugin/skill/MCP: `tafs_sidebar/03-module-notes/plugin-system.md`, `tafs/internal/plugin/`, `tafs/internal/tools/`.
- Model/LLM profiles: `tafs_sidebar/03-module-notes/backend-core.md`, `tafs_sidebar/03-module-notes/worker-agent-tools.md`, relevant `tafs` source.
- Documents/search/RAG/vector direction: `tafs_sidebar/11-terai-current-facts.md`, latest meetings, `terai_ye_sidebar/03-module-notes/knowledge-and-skills.md` only as demo input.
- Frontend/demo comparison: `terai_ye_sidebar/INDEX.md`, `terai_ye_sidebar/02-architecture-map.md`, `terai_ye_sidebar/05-tafs-comparison.md`, then current `terai_ye` source.

## Execution Rules

- Default to Chinese prose; keep commands, paths, fields, and identifiers in English.
- Use evidence: cite files, code, tests, command output, latest meeting records, or explicit user statements.
- Inspect `git status` before edits in any touched Git repo.
- Do not touch unrelated dirty files.
- Treat `/home/ZykLyj/yjdev/tafs` as the default fact/integration source. For code/config/script/runtime-behavior changes, create a Session Worktree under `/home/ZykLyj/yjdev/worktrees/tafs/<branch-slug>/` from an explicit base unless the user explicitly approves another write scope.
- Documentation, skill, and sidebar updates are allowed when the user explicitly asks to write/update docs or preserve a conclusion.
- Every code/config/script/behavior change needs docs-sync review; if no doc update is needed, explain why.
- Never persist credentials, tokens, cookies, private keys, or API keys.

## Completion Checklist

- State the files changed, or say no files were changed.
- Report validation commands and results, or why validation was blocked.
- Report docs-sync outcome.
- For committed work, stage only current-task files and use `type(scope): summary` plus a useful body.
- Push only when remote, credentials, and proxy handling are approved.
