# Terai Adapter

This adapter tells the global agent workflow how to operate across the Terai product workspace:

```text
/home/ZykLyj/yjdev/tafs
/home/ZykLyj/yjdev/tafs_sidebar
/home/ZykLyj/yjdev/terai_ye
/home/ZykLyj/yjdev/terai_ye_sidebar
```

It does not modify those repositories or sidebars by itself.

## Project Language

- `Terai` is the product and project name.
- `tafs` is the high-confidence technical base and evolving framework for formal Terai backend work.
- `terai_ye` is a demo/reference package. Use it for UI/product-demo ideas, packaging clues, API-shape comparison, and migration input. Do not infer formal architecture from it.

## Required Reading

Before Terai conclusions or work, read:

- `$terai-onboarding` (`/home/ZykLyj/.agents/skills/terai-onboarding/SKILL.md`) as the project bootstrap when available.
- The context pack output from `/home/ZykLyj/.agents/skills/terai-onboarding/scripts/context-pack.sh "<task summary>"`.
- Every `[required]` file listed by the helper.
- Latest meeting records when product direction, scope, planning, or decisions are in scope.
- Task-relevant `[source]` and `[route]` files.

`$terai-onboarding` is a project-level bootstrap helper. It lists mandatory entry docs, current facts, and task-specific route hypotheses, but it does not replace current repo facts, command output, tests, Personal Agent OS HITL rules, or data-source boundaries.

## Fact Priority

When facts conflict, use this order:

1. Current user instruction.
2. Current `tafs` source, command output, tests, and deployed `tos-agentd` behavior.
3. Latest Terai meeting records and `tafs_sidebar/11-terai-current-facts.md`.
4. `tafs_sidebar` source analysis.
5. `terai_ye` source and `terai_ye_sidebar` analysis as demo/reference.
6. Older meeting analysis, memory, or chat context.

## Standing Rules

- Default language: Chinese prose; keep commands, paths, fields, and identifiers in English.
- All claims must be based on source code, docs, command output, tests, meeting records, or explicit user statements.
- Inspect `git status` before edits in any touched Git repo.
- Do not touch unrelated dirty files.
- Treat `/home/ZykLyj/yjdev/tafs` as the default fact and integration worktree.
- Use an independent Session Worktree for code/config/script/runtime-behavior changes unless the user explicitly approves another write scope.
- Create Terai Session Worktrees under `/home/ZykLyj/yjdev/worktrees/tafs/<branch-slug>/` from an explicit base; default to local `main` only after verifying the actual integration branch.
- Treat one Terai branch as writable by one AI session at a time.
- Documentation, skill, and sidebar updates are allowed when the user explicitly asks to write/update docs or preserve a conclusion.
- Code/config/script/behavior changes require docs sync review.
- If a semantic change affects API docs, user docs, packaging, or onboarding facts, update the matching docs.
- 提交与分支遵循公司规范（权威源：`tafs_sidebar/terai_code_guide/代码提交规范 revised.md`、`tafs_sidebar/terai_code_guide/合并请求和分支管理规范.md`）：① 一个 MR 只做一件事，合并到 master 用 **Squash 压成一个 commit**，MR 不宜过大；② Commit 用结构化三段式 `type(scope): 摘要(≤50 中文字)` + 可选正文(背景/方案) + 可选 footer（`Fixes BUG-xxx` / `Closes STORY-xxx` / `For STORY-xxx`、`Breaking-Change:`、`Release-Notes:`），`type` ∈ feat/fix/refactor/perf/docs/style/test/build|ci/chore，单仓必带 scope；③ 分支从 `origin/master` 切出、只允许若干后继 commit、**只用 `git pull --rebase origin master` 同步、禁 merge commit（保持线性历史）**，短期分支合并后删除，禁长期个人远程分支，禁提交二进制，版本用 tag 触发构建。
- Push only when the remote, credentials, and proxy handling are available and approved.
- 实现 Terai 模块 / 代码时的编码规范参考：`tafs_sidebar/terai_code_guide/golang_code_guideline.md`（公司 Go 规范）、`go-modern-guidelines`（现代 Go 习语，按 `go.mod` 版本）、`adk-go`（`/home/ZykLyj/yjdev/adk-go`，Google 官方 Go agent 框架，可用 `adk-go-skill` 上手）作为 Go 运行时 / 接口 / 包结构参考。adk-go 仅作编码与 runtime primitives 参考，不整体复制为 Terai 内核（见 `16` 参考栈收敛）。

## Engineering Workflow Mapping

Terai uses two delivery tracks.

Product requirement / new feature track:

```text
terai-onboarding -> grill-with-docs -> to-prd -> to-issues -> triage -> tdd
```

Use this when the work starts from a fuzzy product need, user-facing feature, scope discussion, or multi-agent/task-tracker coordination need.

Architecture refactor / module split track:

```text
terai-onboarding -> grill-with-docs -> per-module ADR/opening brief -> approval -> tdd/behavior lock -> R/S-separated implementation -> review -> docs sync
```

Use this when changing Terai architecture boundaries, extracting modules, or refactoring `tafs` toward `tafs_sidebar/18-terai-target-architecture-task-record-2026-06-18.md`. If the refactor needs multiple agents or project-management tracking, split the approved ADR into issues and triage those slices before implementation.

Code understanding or tutoring:

```text
terai-onboarding -> tafs-mentor -> source verification
```

Bug or incident:

```text
terai-onboarding -> diagnose -> plan -> approval -> tdd/fix -> review
```

## Scope Boundaries

Terai currently spans a formal technical base and demo/reference material.

- Use `tafs` for formal backend architecture, agent runtime, worker isolation, plugin/skill/MCP/tool behavior, and API implementation facts.
- Use `tafs_sidebar` for current facts, source reading maps, meeting analysis, and canonical onboarding.
- Use `terai_ye` and `terai_ye_sidebar` only for demo analysis, UI/product-reference material, packaging clues, and migration candidates.
- Do not continue production work on `terai_ye` unless the user explicitly scopes a demo-only task.

## Current Dirty-Tree Rule

If this adapter is used while `tafs`, `personal-agent-os`, or sidebar workspaces have unrelated modifications, leave them untouched unless the active approved plan explicitly includes those files.

If the current `tafs` branch or worktree is owned by another session, the active session may inspect it read-only but must not edit files, run formatters, stash, commit, checkout, pull, reset, or otherwise mutate that branch. Create a separate Session Worktree and branch for read-write work.
