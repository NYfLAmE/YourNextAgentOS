# Personal Agent OS

> Status: V1 handbook and Runtime v1 implementation repository
> Timezone: Asia/Shanghai

This repository is the global operating handbook for personal agents. It defines roles, workflows, data boundaries, HITL gates, reporting rules, and improvement loops. It is not a daily journal and does not store private work reports.

The private report archive lives in:

```text
/home/ZykLyj/yjdev/personal-agent-journal/
```

## Start Here

- [Domain context](CONTEXT.md): canonical language for Personal Agent OS, the future Runtime, the Control Plane, approvals, autonomy, and tool boundaries.
- [Architecture decisions](docs/adr/): accepted architecture decisions that future Runtime PRDs and implementations must respect.
- [Agent roster](system/agent-roster.md): the six default agent roles and how they cooperate.
- [Shared context contract](system/shared-context-contract.md): how agents exchange facts, assumptions, decisions, and handoffs.
- [Risk and HITL policy](system/risk-and-hitl-policy.md): when agents may continue and when they must stop for human approval.
- [Engineering delivery](workflows/engineering-delivery.md): fuzzy need to PRD, issues, implementation, review, docs, commit, and push.
- [Reporting and planning](workflows/reporting-and-planning.md): daily, weekly, monthly reports, 08:00 planning, 22:00 snapshots, and late-work supplements.
- [Self improvement](workflows/self-improvement.md): feedback ingestion and low-risk automatic workflow refinement.
- [Data source whitelist](data-sources/whitelist.md): only listed sources may be used as report facts.
- [Terra adapter](projects/terra-openclaw-setup-backend.md): project-specific workflow rules for `TerraOpenclawSetupBackend`.
- [Managed user skills](skills/README.md): Git-managed local user skills exposed through `/home/ZykLyj/.agents/skills`.
- [Runtime v1 self-test](docs/runtime-v1-self-test.md): local validation boundary for the first `paos` CLI implementation.
- [V2 automation backlog](backlog/v2-automation.md): cron, email, connector, and automation work intentionally out of V1.

Future Runtime PRDs must start from the domain context and architecture decisions before proposing behavior, schemas, connectors, or execution rules.

## Runtime Implementation

The first `paos` Runtime slice is implemented as a local Go CLI under `cmd/paos/`.

Supported commands:

- `paos scan`: read-only Control Plane reconciliation for `.scratch/**.md`.
- `paos status`: config discovery plus Runtime Task state summary without printing secret values.
- `paos draft <parent>`: LLM Drafting from a ready Issue, approved Plan, or failed Runtime Task into a draft Runtime Task.
- `paos approve <task>`: durable Approval Record creation and transition to `ready`.
- `paos run <task>`: approved Command List execution inside a dedicated Git worktree with Private Runtime Logs outside Git.
- `paos watch`: local polling watcher that reports state and does not call LLM, approve, or run by itself.

Runtime private config defaults to `~/.personal-agent-os/config.yaml`. API keys are referenced through `llm.api_key_env`; secrets must not be committed to this Control Plane.

## V1 Boundaries

The Personal Agent OS handbook still does not implement these broader automation areas:

- cron jobs or background schedulers
- email sending or email reply ingestion
- calendar, browser, or health data connectors
- persistent background agents
- automatic GitHub remote creation

Runtime v1 includes the first local `paos` CLI implementation, but it remains bounded to local Control Plane scanning, LLM Drafting, task-scoped approvals, approved Command List execution, and Private Runtime Logs. It still does not implement external connectors or Builder autonomy.

Both this repository and the journal repository use local Git now. After the GitHub remotes are created and configured, every update should be committed locally and pushed to the configured remote.

## Operating Principles

- Facts before conclusions: every report, plan, and review must cite source references.
- Explicit whitelist: access to a data source does not mean permission to summarize it.
- Plan-approved autonomy: after a detailed plan is approved, agents may execute inside that plan without repeated approvals.
- Risk-based approval: high-risk side effects, scope changes, and policy changes stop for human approval.
- Latest low-risk feedback wins: low-risk template or wording feedback may update the workflow automatically; high-risk feedback becomes a pending decision.

## Core Artifact Fields

All durable artifacts should use Markdown with YAML frontmatter. Templates include these core fields:

```yaml
source_refs: []
confidence: medium
approval_state: draft
risk_level: low
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
```

Use `source_refs` for evidence, not decoration. If a claim cannot be tied to a source, mark it as an assumption or omit it.

## Local Validation

Before considering documentation changes complete:

```bash
git diff --check
find . -name '*.md' -print
```

Before considering Runtime implementation changes complete:

```bash
go test ./...
go run ./cmd/paos --root /home/ZykLyj/yjdev/personal-agent-os status
go run ./cmd/paos --root /home/ZykLyj/yjdev/personal-agent-os scan
```

For link checks without extra tooling, verify every link from this README points to an existing file.
