# Dispatch — Planner Phase

Use this branch only as the configured planner. In V1 that is Codex.

1. Re-verify every Approved-gate item from source. Select the frontier from the declared dependency graph, never directory numbering, modification time, or convenience. If parent and frontier are the same single-slice task, pass the same plan for both.
2. Confirm the worktree is the task-owned branch, has one coordinated writer, is clean, and `HEAD` is the implementation base. Inspect all tracked, staged, unstaged, and untracked state. No pull, merge, rebase, stash, reset, or migration of another owner's changes belongs to dispatch.
3. Define the immutable contract manifest: parent/frontier plans plus any approved spec, issue map, or Accepted ADR the builder must not edit. Exclude an authority that the Approved plan explicitly schedules for docs-sync; the reviewer must still compare its before/after semantics.
4. Verify the approval evidence files actually say full Pre-Start PASS and resolve all decisions/blockers. The helper checks exact plan status and Git invariants; the planner remains responsible for semantic proof.
5. Start the baton. Example:

```bash
python3 "$SKILL_DIR/scripts/relay.py" start \
  --worktree "$ROOT" --task "$PARENT_PLAN" --frontier "$FRONTIER_PLAN" \
  --base HEAD --actor codex --planner codex --builder cursor --reviewer codex \
  --authority "$PARENT_PLAN" --authority "$FRONTIER_PLAN" \
  --approval-evidence "$PARENT_REVIEW" --approval-evidence "$FRONTIER_REVIEW" \
  --suggested-skill coding-agent-delivery-loop --suggested-skill terai-build \
  --suggested-skill tdd
```

Use `restart` instead of `start` only for an existing `accepted`/`blocked` baton after the new frontier or re-approved contract passes the full gate. From `accepted`, a new builder slice pins clean current `HEAD` as its slice base while retaining the first baton's immutable `root_review_base` and all earlier authority/evidence pins. From `blocked`, `restart` must retain the original `assignment_base` so intervening commits remain in the cumulative review surface; it must never hide work by repinning to current `HEAD`. For a parent Final Review with no new build phase, pass `--phase ready_to_review` and the baton's exact `root_review_base`; the helper rejects `HEAD` or any later base. After that Final Review is accepted and the parent plan is exactly `Done`, run `close --worktree "$ROOT" --actor "$PLANNER"`; never close a child-slice acceptance whose distinct parent remains `Approved`.

If `user_decision`/`authority_drift` interrupts an owned execution/review phase, do not use `restart`, whether the worktree is clean or dirty. Preserve any task-owned partial work. After the changed contract and independent Pre-Start evidence are committed and fully Approved on the same worktree/branch, refresh only the authority snapshot while retaining the original base and interrupted owner:

```bash
python3 "$SKILL_DIR/scripts/relay.py" reapprove \
  --worktree "$ROOT" --task "$PARENT_PLAN" --frontier "$FRONTIER_PLAN" \
  --actor "$PLANNER" --approval-evidence "$PARENT_REVIEW" \
  --approval-evidence "$FRONTIER_REVIEW"
```

Then tell the recorded builder/reviewer to invoke this skill; that owner uses `resume` and receives a new lease. A decision/authority block at an unowned clean boundary may use `restart` only with newly changed approval evidence committed after `blocked_head`. `restart` and `reapprove` both reject worktree, branch, Git-common-dir, fixed-base, or blocked-history migration.

Do not edit product code or duplicate plan content into the baton. Dispatch is complete only when `relay.py show` verifies `ready_to_execute` (or the explicitly selected Final Review phase), the emitted authority hashes/base match the inspected sources, and the worktree remains clean.

Report:

```text
任务 <task>/<slice> 的指派阶段已完成；接力棒 <id> 已交给 <next-role>。
请在 <next-role> 中调用 $coding-agent-delivery-loop，无需附加 prompt。
Authority: <plan>@<approval/base SHA>；Base: <SHA>
```

When an accepted slice has no Approved successor yet, report:

```text
任务 <task>/<slice> 已验收；接力棒 <id> 正在 accepted 等待 planner。
下一 frontier <path> 当前为 <status>，尚未达到 Approved，未分发任何实现任务。
请先完成该 frontier 的 Draft→Approved；完成后在 <planner> 中调用 $coding-agent-delivery-loop，无需附加 prompt。
```

After terminal Parent Final Review and `close`, report:

```text
任务 <task> 的 Parent Final Review 已完成；接力棒 <id> 状态为 closed。
Final evidence: <review path>@<SHA>；Root review base: <SHA>。
该 coding delivery loop 已终止，没有 next agent。merge、push、release 仍未被隐式授权。
```
