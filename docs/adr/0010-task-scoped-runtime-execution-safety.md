# Use Task-Scoped Runtime Execution Safety

Runtime execution will run inside a task-scoped Execution Workspace, preferably a dedicated Git worktree, so read-write access does not target a user's main working tree by default. Within that workspace, approved shell execution is represented by repeatable Command Templates rather than unrestricted shell access; default execution starts with an empty environment and may inject only task-scoped Env Profiles recorded in the plan or Approval Record.

Network access is allowed by default for developer workflows, but task plans must record Network Intent and Runtime Logs must capture the command, environment profile reference, timing, exit status, stdout, and stderr. Full logs are intentionally private, long-lived, and not redacted by default; therefore they must live in a private Runtime directory outside the Git-backed Control Plane and must not be treated as report facts unless explicitly brought into scope.
