# Review — Reviewer Phase

Use this branch only as the configured reviewer. In V1 that is Codex, the rules owner and judge. The reviewer writes review/progress records, not product fixes.

1. Run `relay.py show --worktree "$ROOT"`, verify authority and ownership, then `claim --worktree "$ROOT" --actor "$REVIEWER"`. Retain the returned `lease_token` only in this invocation. For a slice, pin the review surface to `assignment_base...implementation_head`, including every implementation and rework round. For Parent Final Review (`task == frontier`), use `root_review_base...implementation_head`; this base was pinned by the first baton and cannot be replaced by a later slice or current `HEAD`. Never review only the last fix commit. Confirm the worktree is clean and enumerate tracked/untracked/staged/unstaged state.
2. Read and apply [code-review](../../code-review/SKILL.md): run independent Standards and Spec axes from the fixed base. Then run every project-specific Architecture/Effect, security, secret, DB, tool-execution, frozen-contract, LLM-facing, live-evidence, docs-sync, and completion gate. Subagents are read-only inputs; the reviewer re-verifies every load-bearing conclusion against source, commands, tests, and repository authority.
3. Audit cumulative drift exhaustively:
   - approved authority and frozen contracts were not rewritten to fit code;
   - every changed file and behavior traces to the plan, with non-goals untouched;
   - target semantics, errors, races, negative/security cases, and acceptance criteria have independent evidence;
   - module ownership, dependency direction, identity/secret boundaries, and project invariants hold;
   - tests/goldens/contracts were not weakened to make the implementation pass;
   - the fixed base was not replaced through merge/rebase/pull.
4. Classify the outcome:
   - **Implementation mismatch inside the Approved contract:** record concrete findings in canonical `review.md`, keep status Blocked, commit only review records, then run `reject --worktree "$ROOT" --actor "$REVIEWER" --lease-token "$LEASE_TOKEN" --findings <review-path> --commit HEAD`. The baton becomes `rework_ready` for the builder.
   - **The authority itself needs a decision/change, mandatory evidence is unavailable, or ownership/authority drift exists:** record facts and impact, then run `block --worktree "$ROOT" --actor "$REVIEWER" --lease-token "$LEASE_TOKEN" --reason <user_decision|authority_drift|evidence|ownership|environment>`. Return to user/re-approval; never convert it into a builder guess.
   - **Pass:** independently rerun required checks, fill the repository Review Gate/DoD/progress evidence, and mark the current frontier exactly `Done`. A child-slice acceptance must leave a distinct parent task `Approved`; only Parent Final Review may mark the parent `Done`. Commit only review/docs state, then run `accept --worktree "$ROOT" --actor "$REVIEWER" --lease-token "$LEASE_TOKEN" --evidence <review-path> --commit HEAD`. The evidence path must be added or changed in this review phase. `accept` permits administrative header changes only on the frontier; all other approved authorities remain byte-identical, and the frontier's normalized contract must remain byte-equivalent.

Review is complete only when every applicable gate has explicit evidence, both generic axes and project-specific axes are accounted for, all findings are either returned or cleared, the review record is committed, the worktree is clean, and the baton transition succeeds.

For rework, report:

```text
任务 <task>/<slice> 第 <cycle> 轮验收未通过；接力棒 <id> 已交回 <builder>。
请在 <builder> 中调用 $coding-agent-delivery-loop，无需附加 prompt。
Findings: <review path>@<SHA>
```

For acceptance, report:

```text
任务 <task>/<slice> 已通过独立验收，接力棒 <id> 状态为 accepted。
验收证据：<review path>@<SHA>。
下一 frontier / Parent Final Review / merge / push / release：<逐项说明当前 gate 与授权状态>。
请在 <planner> 中调用 $coding-agent-delivery-loop，无需附加 prompt。
```
