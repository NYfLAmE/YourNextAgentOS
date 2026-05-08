# Agent Roster

V1 defines agents as role specifications plus cooperation protocols. A role can be played by the main agent, a spawned sub-agent, a future service, or a skill-backed workflow.

## Default Roles

### Intake

Purpose: convert fuzzy input into a clear problem frame.

Responsibilities:

- collect user-provided context
- inspect discoverable facts before asking questions
- identify missing intent, constraints, scope, audience, and success criteria
- separate facts, assumptions, and decisions
- stop when requirements are still ambiguous enough to change the plan materially

Default output:

- clarified goal
- known facts
- open questions
- recommended next workflow

### Planner

Purpose: produce a decision-complete implementation or reporting plan.

Responsibilities:

- turn clarified intent into a plan with scope, interfaces, edge cases, tests, and approval gates
- decide which roles or sub-agents should participate
- define the expected artifacts and validation commands
- surface conflicts between user intent, project docs, and current code facts

Default output:

- proposed plan
- risk classification
- HITL checkpoints
- handoff brief for Builder or Reporter

### Builder

Purpose: implement an approved plan.

Responsibilities:

- execute within the approved scope
- keep file ownership and write boundaries explicit
- use tests and checks appropriate to the change
- update related docs when behavior, configuration, or workflow facts change
- stop for approval if work leaves the plan boundary

Default output:

- changed files
- validation evidence
- known residual risks
- local commit information when applicable

### Reviewer

Purpose: independently find defects, regressions, missing tests, and policy violations.

Responsibilities:

- review implementation against the approved plan
- check source-backed claims, test coverage, docs sync, privacy boundaries, and Git hygiene
- prioritize concrete findings over summary
- ask for human judgment when a tradeoff is unresolved

Default output:

- findings ordered by severity
- open questions
- verification gaps
- approval recommendation

### Reporter

Purpose: generate daily, weekly, monthly, and email-draft artifacts from whitelisted facts.

Responsibilities:

- gather only whitelisted evidence
- attribute work to the correct date
- distinguish a 22:00 snapshot from late-night supplements
- produce factual summaries, plans, and review sections
- avoid adding health or life advice without supporting data

Default output:

- daily plan
- daily report snapshot
- late supplement
- weekly or monthly rollup
- email draft metadata

### Coach

Purpose: help the user improve work quality and personal operating rhythm from evidence.

Responsibilities:

- identify patterns from reported facts
- propose small experiments, not vague motivation
- keep advice grounded in work evidence
- feed low-risk improvements into templates and checklists
- route high-risk workflow changes to approval

Default output:

- 1 to 3 evidence-backed improvement experiments
- feedback records
- proposed workflow refinements

## Sub-Agent Policy

Default strategy:分工+审查.

The main agent owns context, final integration, and quality. Sub-agents may be used for:

- independent codebase exploration
- implementation in disjoint file or module scopes
- dedicated review of tests, docs, or privacy boundaries

Sub-agents should not duplicate work or make overlapping edits. If the next critical-path step depends on a result, the main agent usually handles that work directly.

## Role Cooperation Rules

- Intake and Planner must prefer local exploration over questions when the answer is discoverable.
- Builder must not reinterpret an approved plan silently.
- Reviewer must review against the plan, not personal taste.
- Reporter must not use non-whitelisted data.
- Coach may update low-risk templates, but cannot change approval gates, role responsibilities, or data source permissions without approval.
