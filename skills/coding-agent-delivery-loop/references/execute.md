# Execute — Builder Phase

Use this branch only as the configured builder. In V1 that is Cursor. This explicit skill invocation authorizes only the routed Approved slice; it does not authorize a second slice, a changed contract, landing, push, or release.

1. Run `relay.py show --worktree "$ROOT"`, verify identity/worktree/branch/current HEAD/authority hashes, then run `claim --worktree "$ROOT" --actor "$BUILDER"`. Capture its one-time `lease_token` in memory for this invocation and never report or persist it. `claim` refuses an already owned phase. After the user confirms the old session ended, `takeover --worktree "$ROOT" --actor "$BUILDER"` fences the abandoned token while preserving base, commits, and dirty state. For a cleared `environment`/`evidence`/`ownership` interruption, or after planner `reapprove`, use `resume --worktree "$ROOT" --actor "$BUILDER"`; a changed decision/authority cannot resume until that re-approval transition. Never clean, stash, reset, rebase, or start over to make state look tidy.
2. Read the full Approved parent/frontier contract, progress/review, and any rework findings. Use the pre-agreed seams. Apply [TDD](../../tdd/SKILL.md) one vertical slice at a time and the repository's implementation/validation rules. The builder implements the plan; it does not reinterpret or edit the Approved contract to match the code.
3. Account for every changed tracked/untracked file against the slice. Run every focused, full-project, contract/golden, security, generated-doc, live-provider/device, packaging, and docs-sync check required by the plan and repository. Record exact commands/results and residual evidence gaps in the canonical progress artifact without secrets.
4. Self-check the cumulative diff from the baton's `assignment_base`, then create a focused structured commit containing only the slice. Leave review status Pending/Blocked; the builder cannot write Passed, Accepted, Done, or begin the next frontier.
5. Submit the baton only with a clean worktree and committed evidence. Every supplied canonical evidence path must be added or changed in this claimed phase; an old tracked progress file is not evidence:

```bash
python3 "$SKILL_DIR/scripts/relay.py" submit \
  --worktree "$ROOT" --actor "$BUILDER" --lease-token "$LEASE_TOKEN" --commit HEAD \
  --evidence "<repo-relative-progress-path>"
```

If execution exposes a user decision, contract/architecture change, unavailable mandatory evidence, authority drift, or ownership conflict, persist the discoverable facts where repository rules require, then use `block --worktree "$ROOT" --actor "$BUILDER" --lease-token "$LEASE_TOKEN" --reason <user_decision|authority_drift|evidence|ownership|environment>`. Preserve partial work and report the blocker; do not manufacture a workaround. `environment`, `evidence`, and resolved `ownership` can resume against unchanged authority; decision/authority changes require planner `reapprove`. Any clean boundary restart must retain the original assignment base.

Execution is complete only when every Approved slice acceptance item has implementation evidence, all required checks pass (or the baton is explicitly blocked), docs/progress are synchronized, the focused commit exists, the worktree is clean, and the baton is `ready_to_review`.

Report:

```text
任务 <task>/<slice> 的执行阶段已完成，尚未验收；接力棒 <id> 已交给 <reviewer>。
请在 <reviewer> 中调用 $coding-agent-delivery-loop，无需附加 prompt。
Implementation HEAD: <SHA>；Evidence: <repo paths>
```
