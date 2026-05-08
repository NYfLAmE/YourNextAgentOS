# Engineering Delivery Workflow

This workflow handles new requirements, bugs, refactors, and project delivery.

## State Machine

```text
intake
-> plan
-> PRD
-> issues
-> triage
-> implementation
-> review
-> acceptance
-> docs sync
-> commit
-> push when remote and credentials are approved
```

## Intake

Use Intake when the initial requirement is fuzzy.

Required actions:

- read project entry docs before asking questions
- inspect source and configuration if the answer is discoverable
- ask only questions that materially change scope, behavior, success criteria, or risk
- record the user's decisions

Exit criteria:

- goal is clear
- success criteria are testable
- in-scope and out-of-scope boundaries are known
- important constraints are recorded

## Plan

Use Planner to create a decision-complete plan.

The plan must include:

- summary and desired outcome
- affected subsystem or project adapter
- public interfaces or artifact shapes
- data flow and state transitions when relevant
- edge cases and failure modes
- test plan and acceptance criteria
- HITL checkpoints
- file or directory ownership if sub-agents participate

The plan must be approved before Builder starts implementation unless the user explicitly requests a small direct edit.

## PRD

Create a PRD when the work is larger than a direct fix.

Use [PRD template](../templates/prd.md).

The PRD should capture:

- problem statement
- target user
- user stories
- scope
- non-goals
- acceptance criteria
- evidence and source references

## Issues

Break PRDs into vertical slices.

Use [Issue template](../templates/issue.md).

Prefer slices that deliver end-to-end behavior. Avoid splitting only by layers such as handler/service/model unless the task is a pure internal refactor.

## Triage

Every issue should have:

- one category: `bug`, `enhancement`, `refactor`, `docs`, or `ops`
- one status: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, or `wontfix`
- enough context for a fresh agent to implement without guessing

`ready-for-agent` means:

- behavior is specified
- source references are listed
- tests or validation are defined
- write scope is clear
- approval policy is clear

## Implementation

Builder executes only inside the approved issue or plan.

Rules:

- inspect `git status` before edits
- do not touch unrelated dirty files
- use project-local patterns
- write focused tests for behavior changes
- update docs when code, config, script, API, or workflow semantics change
- use sub-agents only for independent work scopes or review

## Review

Reviewer checks:

- implementation matches plan
- tests cover the acceptance criteria
- docs are synchronized
- new behavior has evidence
- privacy and data source rules are not violated
- Git staging excludes unrelated files

Findings lead. Summary is secondary.

## Acceptance

Acceptance requires:

- relevant tests/checks passed or blocked reasons recorded
- docs updated or no-doc-change reason recorded
- risks and residual gaps stated
- user-facing behavior summarized

## Commit And Push

Local commit is expected after successful changes.

Commit message format:

```text
type(scope): summary

- What changed
- Why it changed
- Validation performed
```

Push only when:

- remote exists
- authentication path is approved
- proxy or environment requirements are handled
- no unrelated files are staged

## Terra Example Dry Run

For a fuzzy Terra requirement:

1. Intake reads the Terra project adapter.
2. Planner asks only non-discoverable requirement questions.
3. PRD records the confirmed behavior and source facts.
4. Issues are split by vertical slice.
5. Triage marks only sufficiently specified slices as `ready-for-agent`.
6. Builder implements after plan approval.
7. Reviewer checks tests, docs, API/Swagger impacts, and Git hygiene.
