# Terra OpenClaw Setup Backend Adapter

This adapter tells the global agent workflow how to operate in:

```text
/home/ZykLyj/yjdev/TerraOpenclawSetupBackend/
```

It does not modify that repository by itself.

## Required Reading

Before Terra repository work, read:

- `docs/ai-collaboration/` all `.md` files
- `docs/AI-ONBOARDING.md`
- `docs/INDEX.md`
- task-relevant topic docs

For provider/model-config work, also follow the docs index into:

```text
docs/modelconfig/implementation/claude/
```

## Standing Rules

- Default language: Chinese prose; keep commands, paths, fields, and identifiers in English.
- All claims must be based on source code, docs, command output, tests, or explicit user statements.
- Inspect `git status` before edits.
- Do not touch unrelated dirty files.
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
grill-with-docs -> to-prd -> to-issues -> triage -> tdd
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
