# Runtime v1.1 Uses Controlled Context Expansion Before Builder Automation

Runtime v1 already proves a bounded loop: discover Control Plane artifacts, draft Runtime Tasks with an OpenAI-compatible LLM, require an Approval Record, run an approved Command List in a dedicated worktree, and keep full execution logs in Private Runtime Logs. Runtime v1.1 may improve draft quality by expanding context, but that expansion must stay explicit, auditable, and separate from Builder automation.

## Decision

Runtime v1.1 will add controlled context expansion for LLM Drafting through two bounded inputs:

- `source_refs` resolver: reads explicit references from the parent Issue, Plan, PRD, or failed Runtime Task and resolves only allowed repo-local paths.
- project adapter context pack: adds project-specific workflow and reading rules, such as the Terra/OpenClaw adapter and `$terra-onboarding`, without treating adapter output as a substitute for current files, tests, or command output.

The expanded LLM Payload must record what was included, what was excluded, and why. It must not read Private Runtime Logs, private config, credentials, unapproved external data sources, or arbitrary project source trees by default.

Runtime v1.1 will also make Runtime Task Drafts TDD-aware. A draft for implementation work must include RED, GREEN, and REFACTOR/validation intent, but the model still produces a reviewable draft only. TDD is an execution requirement for subsequent Builder work, not a suggestion.

`paos watch` remains report-only by default. Any future watcher-assisted drafting must be an explicit opt-in mode, may create draft Runtime Tasks only, and must not approve or run them.

Runtime v1.1 does not introduce unattended Builder automation. Any code, config, script, runtime-state, or behavior change still requires a task-scoped Approval Record that approves the exact execution boundary.

## Consequences

- LLM Drafting can become more useful without silently exporting whole repositories or private runtime data.
- `source_refs` become operational evidence inputs rather than decorative metadata.
- Project adapters define mandatory reading and policy context, but current repo files, code, tests, and command output remain the fact boundary.
- Runtime Task Draft schema and templates need room for context-pack evidence and TDD steps.
- Watcher behavior stays compatible with current v1 tests that assert `watch --once` does not call the LLM or write files.
- Builder-style file modification remains a future design problem unless a specific approved Runtime Task permits exact commands in an Execution Workspace.

## Non-Decisions

- This ADR does not approve automatic command execution from watcher events.
- This ADR does not approve reading Private Runtime Log contents into LLM Payloads.
- This ADR does not approve external connectors such as email, calendar, browser history, chat, or remote issue trackers.
- This ADR does not approve broad shell access, global autonomy, or credential handling.

## Source References

- `../../CONTEXT.md`: domain terms for Runtime, Control Plane, Runtime Task Draft, LLM Payload, Approval Record, Execution Workspace, Command List, and Private Runtime Log.
- `0010-task-scoped-runtime-execution-safety.md`: approved execution boundary, worktree, command, environment, network, and private log rules.
- `0014-llm-drafting-in-runtime-v1.md`: v1 LLM Drafting boundary and default exclusion of source files and Private Runtime Logs.
- `../runtime-v1-self-test.md`: current implemented self-test boundary.
- `../runtime-v1-tdd-hardening.md`: current tested behavior matrix, remaining gaps, and RED/GREEN rule.
- `../../projects/terra-openclaw-setup-backend.md`: Terra adapter reading and policy boundary.
- `../../../TerraOpenclawSetupBackend/docs/ai-collaboration/workflow-rules.md`: Terra rule that code/config/script/runtime-state/behavior changes require approval and fact-based evidence.
