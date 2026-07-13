# Engineering Delivery Workflow

This workflow handles new requirements, bugs, refactors, and project delivery.

## State Machine

```text
intake
-> plan
-> spec
-> tickets
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

## Communication Efficiency

When explaining non-trivial technical behavior to a human, use progressive disclosure before reference detail.

**Hard rule — explain by scenario before terminology (2026-06-24 user feedback).** Before introducing any concept, design, mechanism, or option, first answer in one or two plain sentences: *what real scenario triggers it, and what concretely goes wrong without it*; then say what it does; only then name interfaces, fields, or identifiers. Gloss every jargon/English term (e.g. `flat threshold`, `pair-safe`, `cooldown`, `snapshot`, `idempotent`) in plain language at first use. Never dump multiple unexplained terms — one extra sentence of scenario beats one more piece of jargon. Default to the user's language (Chinese here); keep only unavoidable identifiers in English, each with an inline gloss.

Required shape:

1. Start with a one-sentence mental model in the user's vocabulary.
2. Give the core process in 2-4 semantic chunks. Each chunk should group low-level fields, commands, or implementation details into one meaningful operation, such as "encrypt the body with AES-GCM" before listing `ciphertext`.
3. Then map those chunks to exact endpoints, fields, files, commands, or error cases.
4. Put exhaustive schema tables, edge cases, and code after the mental model unless the user explicitly asks for reference detail first.

For API, protocol, security, or architecture explanations:

- explain "what happens" and "who owns which data/key/state" before listing fields
- prefer task verbs over inventory phrasing, for example "generate key -> encrypt body -> wrap key -> send envelope"
- keep the first-pass flow restatable in three bullets or fewer
- separate explanation from reference; do not bury the main process inside a field-by-field table
- preserve factual precision by moving constraints and failure modes into the follow-up detail layer, not by omitting them

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

`triage` is an intake path for incoming external or raw requests, not a mandatory hop after ticket generation.

## Spec

Create a spec when the work is larger than a direct fix and the important decisions are already established. Use `/to-spec`; it synthesizes the conversation rather than reopening discovery.

The existing [PRD template](../templates/prd.md) remains a compatibility template until its file name is migrated.

The spec should capture:

- problem statement
- target user
- user stories
- scope
- non-goals
- acceptance criteria
- evidence and source references

Do not mark a spec ready for implementation before the target project's approval gates pass.

## Tickets

Use `/to-tickets` to break a spec, plan, or confirmed conversation into tracer-bullet tickets.

Use the existing [Issue template](../templates/issue.md) as the compatibility body shape when the configured tracker has no stronger native form.

Each ticket should deliver end-to-end behavior, fit one fresh context, and declare every blocking edge. The open, unblocked tickets form the frontier. Avoid splitting only by layers such as handler/service/model unless the task is a wide mechanical refactor; use expand-contract for that exception.

## Triage

Use triage for incoming issues, bug reports, enhancement requests, and external contributions that have not already been aligned and decomposed. Tickets produced by `/to-tickets` do not need a second triage pass; they become ready only when the target project's approval gate says so.

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

Use `/implement` for one approved frontier ticket or one approved single-session plan. Pin the base commit before edits so review has a fixed point.

Rules:

- inspect `git status` before edits
- perform read-write interactive work inside a Session Worktree, not another session's working tree
- declare the base branch or commit before creating a Session Worktree
- use `/home/ZykLyj/yjdev/worktrees/<repo>/<branch-slug>/` as the default Session Worktree root
- treat one branch as writable by one AI session at a time; other sessions stay read-only or create their own branch
- wait for another session to publish a commit, push, or explicit patch before depending on its uncommitted changes
- do not touch unrelated dirty files
- use project-local patterns
- write focused tests for behavior changes
- update docs when code, config, script, API, or workflow semantics change
- use sub-agents only for independent work scopes or review

### Session Worktree Integration Flow

Use one integration worktree for the integration branch, such as `dev` or `main`, and separate Session Worktrees for feature or bugfix branches.

Default flow:

1. Confirm the integration worktree is on the intended integration branch and has no tracked changes.
2. Create a feature branch and Session Worktree from the integration branch.
3. Do implementation, validation, docs sync, and commit work inside the feature Session Worktree.
4. Return to the integration worktree and merge the completed feature branch.
5. Continue work in other feature Session Worktrees only after manually merging the updated integration branch, or rebasing when the project explicitly allows it.

Merging a feature branch into the integration branch updates the shared Git ref. It does not automatically rewrite the working tree or index of other Session Worktrees.

## Review

Use `/code-review` for independent Standards and Spec axes. Then run any project-specific architecture, effect, security, approval, or completion gate. Reviewer checks:

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
3. The spec records the confirmed behavior and source facts.
4. Tickets are split by vertical slice with blocking edges.
5. The project approval gate marks only sufficiently specified frontier tickets as ready.
6. `/implement` builds one approved ticket from a pinned base.
7. Reviewer checks tests, docs, API/Swagger impacts, and Git hygiene.
