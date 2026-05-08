# Shared Context Contract

All agents share a common context model. The goal is to prevent role-specific agents from drifting apart or inventing facts.

## Context Classes

Use these labels in plans, reports, handoffs, and reviews:

- `Fact`: verified by a source reference such as a file, command output, commit, session log, or user statement.
- `Assumption`: reasonable but not verified; must say how to verify.
- `Decision`: explicitly chosen by the user or by an approved plan.
- `Constraint`: a boundary that must not be crossed.
- `Risk`: a possible failure mode or side effect.
- `Open Question`: a decision that still needs user input or further evidence.

## Required Handoff Shape

When one role hands work to another, include:

```yaml
task:
current_state:
facts: []
assumptions: []
decisions: []
constraints: []
risks: []
open_questions: []
allowed_actions: []
forbidden_actions: []
expected_outputs: []
validation:
```

## Source References

Valid source references include:

- absolute or repo-relative file paths
- Git commit hashes
- command names plus summarized output
- Codex session or rollout summary paths
- journal report paths
- explicit user statements from the current conversation

Do not use "I remember" as a source. If memory is useful, cite the memory file or re-verify the fact.

## Date Attribution

Reports use Asia/Shanghai dates.

- Work before 22:00 belongs to the current natural date.
- Work after 22:00 still belongs to the current natural date until local midnight.
- The 22:00 daily email is a snapshot, not a final seal.
- Late-night work after the 22:00 snapshot is recorded as a late supplement and surfaced in the next 08:00 plan email.

## Conflict Resolution

When sources conflict:

1. Current user instruction wins over older workflow defaults unless it violates a higher-priority rule.
2. Current code, command output, and files win over older summaries.
3. Explicit decisions win over assumptions.
4. For low-risk feedback, the newest feedback wins.
5. For high-risk feedback, create a pending decision and stop before changing the canonical workflow.
