# Data Source Whitelist

Only sources listed here may be used as facts for reports, plans, and review sections.

The machine may contain many readable files. Readability is not consent.

## Enabled In V1

### Codex Sessions

Allowed paths:

```text
/home/ZykLyj/.codex/sessions/
```

Allowed use:

- extract user-agent conversations
- identify tasks discussed on a given Asia/Shanghai date
- cite session path and timestamp

Restrictions:

- do not quote sensitive values
- do not treat a partial session as complete without checking timestamps

### Codex Memory Summaries

Allowed paths:

```text
/home/ZykLyj/.codex/memories/MEMORY.md
/home/ZykLyj/.codex/memories/rollout_summaries/
```

Allowed use:

- summarize completed tasks and durable conclusions
- cross-check dates, commits, and validation evidence

Restrictions:

- memory is secondary to current files and command output
- stale facts must be re-verified when they affect a current decision

### Git Metadata In Local Repositories

Allowed use:

- `git log`
- `git status`
- `git diff --stat`
- commit hashes and messages

Restrictions:

- do not include unrelated dirty work as completed work
- do not infer user intent from commit messages alone

### Current Conversation

Allowed use:

- explicit user statements
- approved plans
- user feedback
- decisions made in the active session

Restrictions:

- distinguish user intent from agent inference

### Journal Repository

Allowed path:

```text
/home/ZykLyj/yjdev/personal-agent-journal/
```

Allowed use:

- daily, weekly, monthly reports
- feedback records
- email drafts
- manually added work notes

Restrictions:

- this repository is private by default
- do not copy private report content into public project docs

### Project Files Explicitly In Scope

Allowed use:

- source files, docs, tests, and configs for a project named in the active task
- command output from read-only or approved checks

Restrictions:

- do not summarize unrelated projects just because they are nearby
- obey each project adapter and repository-specific rules

## Disabled Until Explicitly Approved

These sources are not enabled in V1:

- direct mailbox access
- calendar connectors
- browser history
- chat/IM history
- health, sleep, exercise, or wearable data
- financial accounts
- cloud drive contents
- system-wide activity logs outside Codex and approved project commands

## Adding A Data Source

Adding a source is high-risk and requires approval.

The proposal must include:

- source path or connector
- exact allowed fields
- retention rule
- privacy risks
- report sections that may use it
- examples of facts it can and cannot support
