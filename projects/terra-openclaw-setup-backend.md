# Terra OpenClaw Setup Backend Adapter

This adapter tells the global agent workflow how to operate in:

```text
/home/ZykLyj/yjdev/TerraOpenclawSetupBackend/
```

It does not modify that repository by itself.

## Required Reading

Before Terra repository work, read:

- `$terra-onboarding` (`/home/ZykLyj/.agents/skills/terra-onboarding/SKILL.md`) as the project bootstrap when available.
- `docs/ai-collaboration/` all `.md` files
- `docs/AI-ONBOARDING.md`
- `docs/INDEX.md`
- task-relevant topic docs

`$terra-onboarding` is a project-level bootstrap helper. It lists mandatory entry docs, linked candidates, and task-specific route hypotheses, but it does not replace current repo facts, command output, tests, Personal Agent OS HITL rules, or data-source boundaries.

For provider/model-config work, also follow the docs index into:

```text
docs/modelconfig/implementation/claude/
```

## Standing Rules

- Default language: Chinese prose; keep commands, paths, fields, and identifiers in English.
- All claims must be based on source code, docs, command output, tests, or explicit user statements.
- Inspect `git status` before edits.
- Do not touch unrelated dirty files.
- Use an independent Session Worktree for any read-write interactive AI work.
- Create Terra Session Worktrees under `/home/ZykLyj/yjdev/worktrees/TerraOpenclawSetupBackend/<branch-slug>/` from an explicit base; default to local `dev` unless the user specifies another base.
- Treat one Terra branch as writable by one AI session at a time.
- Treat `/home/ZykLyj/yjdev/TerraOpenclawSetupBackend` on local `dev` as the default integration worktree; use it for creating feature worktrees, merging, validation, and push rather than feature development.
- After a feature branch merges into local `dev`, other Terra Session Worktrees must explicitly merge `dev` or use an approved rebase flow before assuming they have the latest integrated files.
- Code/config/script/behavior changes require docs sync review.
- If a semantic change affects API docs or Swagger, regenerate and validate the docs as the project requires.
- Commit messages should use `type(scope): summary` plus a useful body.
- Push only when the remote and credentials are available and approved.

## Engineering Workflow Mapping

Fuzzy new requirement:

```text
Intake -> Planner -> PRD -> Issues -> Triage -> Builder -> Reviewer
```

Useful local skill flow:

```text
terra-onboarding -> grill-with-docs -> to-prd -> to-issues -> triage -> tdd
```

Bug or incident:

```text
diagnose -> plan -> approval -> tdd/fix -> review
```

## Scope Boundaries

Terra is one repository inside a multi-repo workspace.

When work crosses boundaries, inspect the sibling source explicitly:

- packaging/install/nginx: `../terraclaw_worktrees/accumulateWithoutAppAndDirChange/`
- upstream OpenClaw behavior: `../openclaw/`
- TAI backend comparison: `../tai-backend/`

Do not infer sibling behavior from Terra docs alone.

## Current Dirty-Tree Rule

If this adapter is used while Terra or packaging worktrees have unrelated modifications, leave them untouched unless the active approved plan explicitly includes those files.

If the current Terra branch or worktree is owned by another session, the active session may inspect it read-only but must not edit files, run formatters, stash, commit, checkout, pull, reset, or otherwise mutate that branch. Create a separate Session Worktree and branch for read-write work.
