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
- Commit messages should use `type(scope): summary` plus a useful body.
- Push only when the remote, credentials, and proxy handling are available and approved.

## Engineering Workflow Mapping

Fuzzy new requirement:

```text
terai-onboarding -> grill-with-docs -> to-prd -> to-issues -> triage -> tdd
```

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
