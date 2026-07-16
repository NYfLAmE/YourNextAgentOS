---
name: coding-agent-delivery-loop
description: Explicitly advance one Approved coding build task through assignment, implementation, and independent acceptance, one agent phase at a time.
disable-model-invocation: true
---

# Coding Agent Delivery Loop

Carry one **baton** through `planner -> builder -> reviewer`; advance exactly one phase per invocation. The repository remains authoritative for scope, decisions, findings, evidence, and completion. The baton stores only routing metadata and hashes.

## 1. Recover the baton

Treat the directory containing this file as `SKILL_DIR`. Establish agent identity only from the trusted runtime/system context. V1 roles are `codex = planner + reviewer` and `cursor = builder`; an unknown agent is read-only until the user explicitly changes the role policy.

Run:

```bash
python3 "$SKILL_DIR/scripts/relay.py" show --worktree "<task-worktree>"
```

Resolve the project router before treating the current Git root as a task worktree. A dedicated task worktree may be used directly; a project's canonical intake checkout may not. In particular, `/home/ZykLyj/yjdev/terai` is always a read-only routing anchor even when it is the current Git root. Outside a task worktree, omit `--worktree` only when exactly one discoverable baton exists. Ambiguity is a hard stop; never select the newest task.

If `show` returns `no_baton`, do not ask the user to restate the task. Only the planner may bootstrap routing. Use a dedicated current worktree if one exists; otherwise read the Personal Agent OS project adapter and its router. For Terai, inspect `git worktree list --porcelain` from the intake anchor and apply `terai-build`'s Worktree Intake Gate to every plausible active effort. Bootstrap only when exactly one task worktree has a fully Approved parent and frontier and no conflicting writer. Zero eligible worktrees is `[NOT_APPLICABLE]`; more than one is `[AMBIGUOUS]`. If repository progress, commits, or dirty state show post-approval work but its baton is missing, report an ownership conflict and require manual reconstruction from the original fixed base; never invent a new baton/base from current `HEAD`.

## 2. Rebuild authority

Read the selected repository's instructions and its current task, frontier, progress, review, spec/issue, ADR, architecture, and Git evidence. Before any baton mutation, read [the shared context contract](../../system/shared-context-contract.md) and [handoff rules](../handoff/SKILL.md); keep secrets out and reference existing artifacts instead of copying them.

For Terai, also read [terai-build](../terai-build/SKILL.md), [all mandatory gates](../terai-build/references/gates.md), and the selected worktree's current `AGENTS.md` plus task-relevant `docs/` and `arch/`. Project authority overrides this generic relay.

## 3. Enforce the Approved gate

With no baton, assignment is eligible only when all of these are proven from current sources:

- the parent task and exactly one current frontier plan have a canonical status field whose whole value is `Approved`;
- their approval records cover the slice, independent Pre-Start review explicitly passes, and every Decision-needed, Blocker, and Open Question is resolved;
- every predecessor required by the dependency graph is accepted with its checkpoint commit;
- the recorded worktree, branch, approved base, and writer ownership agree with Git; the handoff boundary is clean.

Canonical means either a column-zero root YAML `status`/`approval_state` inside exact `---` delimiters, or the column-zero status blockquote as the first nonblank line after a Markdown H1. Nested examples, lists, comments, HTML, fences, malformed frontmatter, and later body text never count. An occurrence of the word `Approved` or a partial/draft `PASS` proves nothing. When any condition fails, emit `[NOT_APPLICABLE]` with source-backed reasons and perform zero baton/project mutation. An active baton whose authority or ownership no longer verifies is `blocked`, never guessed past.

## 4. Execute only the routed phase

- No baton + proven gate, or an accepted baton with a newly Approved frontier: only the planner reads and follows [dispatch](references/dispatch.md).
- `ready_to_execute`, `executing`, `rework_ready`, or `reworking`: only the configured builder reads and follows [execute](references/execute.md).
- `ready_to_review` or `reviewing`: only the configured reviewer reads and follows [review](references/review.md).
- `blocked`: the planner reports and coordinates the named gap. If its reason is `environment`, `evidence`, `ownership`, or internal `reapproved`, the blocker is now demonstrably cleared, and the current agent is the recorded interrupted owner, that owner reads [execute](references/execute.md) or [review](references/review.md) as appropriate and uses `resume`; a changed decision/authority must first pass full re-approval and the planner's `reapprove` transition. Otherwise perform no project mutation.
- `accepted`: report acceptance and any still-unapproved next frontier, merge, push, or release gate.
- `closed`: report terminal parent completion; no next coding phase is authorized.

If the current agent does not own the routed role, perform no mutation and tell the user which configured agent must receive the baton.

## 5. Handoff

Every successful transition regenerates a redacted temporary handoff view under the current user's `$XDG_RUNTIME_DIR` (fallback `$TMPDIR/coding-agent-delivery-loop-<uid>/`). The authoritative routing baton persists under `$XDG_STATE_HOME/coding-agent-delivery-loop/` (fallback `~/.local/state/coding-agent-delivery-loop/`); both locations have environment overrides for isolated tests. Managed roots must be real, current-user-owned directories, never symlinks. The handoff is derived and may be regenerated by `show`; never reconstruct state from it. Read the emitted handoff path before reporting. Except for terminal `closed`, finish with the exact task/slice, phase, baton id, authority/base or implementation HEAD, and this instruction:

```text
请在 <next-agent> 中调用 $coding-agent-delivery-loop，无需附加 prompt。
```

Completion means one phase met every checkable criterion in its branch file and the baton JSON changed under its lock through an atomic file replacement. Nonterminal completion also requires the next-agent instruction; terminal `closed` instead requires an explicit no-next-phase report. Only reviewer acceptance may call a slice accepted; repository Final Review/DoD alone may call the parent task done.

## 6. Safety boundary

Lease tokens fence concurrent sessions of the same named agent but remain a cooperative workflow control, not operating-system authentication. Keep the raw token only in the claiming invocation; never write it to Git, the baton, the handoff, or the completion report. `takeover` is allowed only after the human has confirmed the old session ended and invalidates its token. The helper cannot stop direct Git edits, and total loss/corruption of external baton state requires source-backed manual reconstruction and re-approval. Baton metadata contains paths, task names, and evidence references, so none of those names may contain secrets or sensitive values.
