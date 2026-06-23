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

## Sidebar Sync Rules

- Treat `/home/ZykLyj/yjdev/tafs_sidebar` as the durable sidecar for Terai architecture, source analysis, meeting-derived decisions, route decisions, and recurring bug/risk findings.
- When a Terai discussion produces a new decision, supersedes an older conclusion, or changes the recommended route, update the matching `tafs_sidebar` document in the same turn when the user asks to preserve or sync the conclusion.
- If an answer relies on an older `tafs_sidebar` conclusion that current source or current user instruction supersedes, update the sidecar or explicitly say why no update was made.
- For current-source `tafs` analysis, use a write-through rule: if the analysis produces a new behavior fact, architecture conclusion, bug/risk, or supersedes an older conclusion, update the closest `tafs_sidebar` document in the same turn by default. If no durable update is needed, say why.
- Prefer updating existing canonical files first: `11-terai-current-facts.md` for current facts, route-decision docs for architectural direction, module notes for source-level findings, and `INDEX.md` for discovery/routing.
- Add a new sidebar document only when the conclusion spans multiple existing docs or needs a stable decision record of its own.
- Do not update `tafs_sidebar` for every casual thought; update it for decisions, current-source facts, repeated diagnosis findings, architecture direction, and work rules that future agents or teammates should reuse.
- Sidecar updates are documentation changes and are allowed when the user explicitly asks to write/update docs or preserve a conclusion. They still require source-backed wording and a docs-sync note in the final response.

## Architecture Writing Rules

- For Terai architecture docs, prefer Chinese explanatory names first, with English identifiers in backticks only when they help map to code or future interfaces.
- Avoid relying on abstract English terms alone. If a term like `materialize`, `surface`, `binding`, `snapshot`, `provider-visible`, or `executor registry` appears, explain it in plain Chinese nearby.
- Preferred wording examples:
  - `materialize` -> `生成本次运行快照`
  - `AgentSurfaceSnapshot` -> `本次 Agent 可见能力快照`
  - `provider-visible tool definitions` -> `模型/API 可见的工具定义`
  - `hidden executor registry` -> `后端执行器映射，模型不可见`
  - `surface binding` -> `能力如何投射到用户界面或 Agent 可见能力`
- For supervisor-facing or teammate-facing explanations, answer “这个模块为什么存在、解决什么问题、运行时发生什么” before listing interface names.
- Keep architecture writing source-backed and precise, but do not make the wording more bookish than necessary.

## Architecture Concept Introduction Rules

When discussing or documenting Terai architecture, do not introduce a new concept, module, struct, field, event, or identifier just because another agent framework uses it.

Before a new architecture concept enters a target architecture doc or interface proposal, answer these checks:

- What concrete product or engineering scenario requires it?
- Why can existing Terai concepts not carry that responsibility?
- Which module owns it, who creates it, who consumes it, and who persists it?
- Is it part of V1, or only a V2+ candidate?
- Can the name be simpler or explained with a Chinese descriptive term first?
- Does it introduce migration, privacy, audit, storage, UI, or evaluation complexity?
- If it is only a future capability, can the current design use a lighter anchor/ref instead of a full snapshot/store/schema?

If a concept does not pass this necessity check, keep it out of the target architecture and record it only as an open question or future candidate.

## Architecture Reference Research Rules

For Terai architecture-level discussions, before the next analysis, grill, or decision step, first delegate focused sub-agents to research mature agent products, frameworks, or architecture references when such references can reasonably inform the question.

Use this rule for module boundaries, naming, data flow, state machines, context / memory / prompt, runtime, capability, provider, observability, approval, security policy, and other target-architecture decisions.

Each delegated research result must be traceable and must separate `Fact`, `Inference`, and `Recommendation`. It should include local source paths or document paths, line numbers or stable anchors where available, and an explicit mapping back to the relevant Terai modules.

Do not use this rule for pure current-source fact lookup, obvious small wording edits, user instructions that explicitly skip external/reference research, or cases where no mature reference source is available. If this rule is skipped for an architecture topic, state why.

## Task Routing

- Fuzzy requirement: use `grill-with-docs` after onboarding; ask only questions that change scope, behavior, success criteria, or risk.
- Old code understanding or source tutoring: use `tafs-mentor` after onboarding. Keep `tafs-mentor` focused on code explanation and learning notes.
- Bug, incident, failing test, or performance issue: use `diagnose`; reproduce or build a read-only evidence loop before root-cause claims.
- Clear implementation issue: use `tdd`; propose interface, tests, risks, and acceptance before editing unless the user explicitly requested a small direct edit.
- Architecture review or refactor opportunity: use `improve-codebase-architecture`; default to read-only findings first.
- PRD or issue work: use `to-prd`, `to-issues`, or `triage`; use local Markdown unless the user explicitly requests a remote tracker.

## Common Source Routes

- Project direction/current facts: `tafs_sidebar/10-terai-onboarding-workflow.md`, `tafs_sidebar/11-terai-current-facts.md`, latest `tafs_sidebar/meeting_log/*_Terai.txt`.
- Architecture route/reference stack: `tafs_sidebar/13-terai-clean-architecture-route-decision.md`, `tafs_sidebar/16-terai-reference-stack-convergence-2026-06-17.md`, `tafs_sidebar/14-agent-framework-reference-survey-2026-06-16.md`, `tafs_sidebar/15-coding-agent-product-reference-2026-06-16.md`.
- tafs architecture: `tafs_sidebar/INDEX.md`, `tafs_sidebar/17-current-service-chain-and-module-map-2026-06-18.md`, `tafs_sidebar/02-architecture-map.md`, `tafs/internal/httpapi/router.go`, `tafs/internal/worker/`, `tafs/internal/agent/`.
- Chat/agent flow: read `tafs_sidebar/17-current-service-chain-and-module-map-2026-06-18.md` first for `serve` / `Supervisor` / parent-side `Worker` / worker `child` / `agent` boundaries, then `tafs_sidebar/09-chat-flow-mainline.md` and `tafs_sidebar/03-module-notes/worker-agent-tools.md`.
- Plugin/skill/MCP: `tafs_sidebar/03-module-notes/plugin-system.md`, `tafs/internal/plugin/`, `tafs/internal/tools/`.
- Model/LLM profiles: `tafs_sidebar/03-module-notes/backend-core.md`, `tafs_sidebar/03-module-notes/worker-agent-tools.md`, relevant `tafs` source.
- Documents/search/RAG/vector direction: `tafs_sidebar/11-terai-current-facts.md`, latest meetings, `terai_ye_sidebar/03-module-notes/knowledge-and-skills.md` only as demo input.
- AI search / Terai search integration: `tafs_sidebar/19-ai-search-service-integration-guide-2026-06-21.md`, `tafs_sidebar/11-terai-current-facts.md`, `tafs_sidebar/18-terai-target-architecture-task-record-2026-06-18.md`. Current route is UI-first, tool-second: first expose `ai_search` as a standalone Terai UI module with trusted backend/user injection, then register the same capability as a conversation tool through `Capability Module` / `CapabilityRuntime`.
- Context / memory / session architecture: `tafs_sidebar/21-terai-context-memory-module-2026-06-23.md`, `tafs_sidebar/18-terai-target-architecture-task-record-2026-06-18.md`, `tafs_sidebar/20-terai-observability-module-2026-06-22.md`. Current route is `Context & Memory Module` with `Session Domain` / `Context Domain` / `Memory Domain`; V1 uses `RunEvent/EventLog` as AgentRun fact source, `Conversation Display Projection` for UI history, and lightweight `ContextAnchor` instead of full `ContextSnapshot`. `Prompt Assembly Module` is a sibling module: `Prompt Rendering Pipeline` consumes `ContextPackage` and produces `PromptBundle`; older docs that mention `PromptContext Pipeline` should be read as this rendering pipeline.
- Frontend/demo comparison: `terai_ye_sidebar/INDEX.md`, `terai_ye_sidebar/02-architecture-map.md`, `terai_ye_sidebar/05-tafs-comparison.md`, then current `terai_ye` source.

## Execution Rules

- Default to Chinese prose; keep commands, paths, fields, and identifiers in English.
- Use evidence: cite files, code, tests, command output, latest meeting records, or explicit user statements.
- Inspect `git status` before edits in any touched Git repo.
- Do not touch unrelated dirty files.
- Treat `/home/ZykLyj/yjdev/tafs` as the default fact/integration source. For code/config/script/runtime-behavior changes, create a Session Worktree under `/home/ZykLyj/yjdev/worktrees/tafs/<branch-slug>/` from an explicit base unless the user explicitly approves another write scope.
- Documentation, skill, and sidebar updates are allowed when the user explicitly asks to write/update docs or preserve a conclusion.
- Every code/config/script/behavior change and every current-source architecture analysis needs docs-sync review; if no doc update is needed, explain why.
- Never persist credentials, tokens, cookies, private keys, or API keys.

## Completion Checklist

- State the files changed, or say no files were changed.
- Report validation commands and results, or why validation was blocked.
- Report docs-sync outcome.
- For committed work, stage only current-task files and use `type(scope): summary` plus a useful body.
- Push only when remote, credentials, and proxy handling are approved.
