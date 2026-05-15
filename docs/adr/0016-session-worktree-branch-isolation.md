# Use Session Worktrees For Interactive AI Branch Isolation

Interactive AI development sessions will use a Session Worktree: a dedicated Git worktree plus a dedicated branch owned by one session at a time. This keeps read-write development out of another session's dirty working tree while still sharing the repository object database and local refs.

## Decision

For interactive project work that writes code, configuration, scripts, documentation, or workflow semantics, the default workspace is a Session Worktree.

- The default root is `/home/ZykLyj/yjdev/worktrees/<repo>/<branch-slug>/`.
- Each session must declare an explicit base branch or commit before creating the worktree.
- One branch is writable by only one AI session at a time.
- If another session owns a dirty branch or worktree, later sessions may inspect it read-only but must not edit, format, stash, commit, checkout, pull, reset, or otherwise mutate it.
- If new work depends on another session's uncommitted changes, the default is to wait for that session to publish a commit, push, or explicit patch. Copying an uncommitted diff is not the default.
- Integration branches such as `dev` or `main` should be managed from an integration worktree. Feature Session Worktrees merge back there after their commits and validation are complete.
- A merge into the integration branch updates the shared Git ref, but other Session Worktrees keep their own working tree and index until they explicitly merge or rebase the updated integration branch.

This does not replace the Runtime **Execution Workspace** concept. Execution Workspace remains the task-scoped worktree used by approved Runtime Tasks. Session Worktree is for interactive AI development before or outside Runtime execution.

## Consequences

- Multiple AI sessions can work in parallel without competing for the same working directory.
- Dirty user or AI changes remain isolated and visible instead of being overwritten by checkout, format, stash, reset, or commit commands from another session.
- Branch ownership becomes an explicit coordination boundary.
- Integration responsibility is separated from feature development responsibility.
- Git worktree is preferred over full clone because it is lightweight, shares local objects and refs, and preserves one repository identity.
- Full clone remains available only when stronger repository-level isolation is explicitly needed.
- Shared branch editing and copied dirty diffs remain exceptional cases requiring explicit human approval.

## Non-Decisions

- This ADR does not define automatic cleanup of old Session Worktrees.
- This ADR does not grant unattended command execution or broader Runtime autonomy.
- This ADR does not change credential, network, push, or remote-write approval policy.
- This ADR does not require all read-only analysis to happen inside a Session Worktree.
- This ADR does not force every project to use `dev`; each project adapter may name its own integration branch.

## Source References

- `../../CONTEXT.md`: domain terms for Execution Workspace, Runtime Task, Approval Record, and Session Worktree.
- `0010-task-scoped-runtime-execution-safety.md`: Runtime Execution Workspace boundary.
- `../../workflows/engineering-delivery.md`: implementation workflow and Git hygiene rules.
- `../../../TerraOpenclawSetupBackend/docs/ai-collaboration/workflow-rules.md`: Terra repository collaboration and dirty-tree rules.
