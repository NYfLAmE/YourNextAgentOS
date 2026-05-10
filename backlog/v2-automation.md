# V2 Automation Backlog

V1 defines the workflow. V2 implements automation.

Before writing Runtime PRDs or implementation plans, read the [domain context](../CONTEXT.md) and [architecture decisions](../docs/adr/). Runtime work must preserve the Git-backed Markdown Control Plane, task-scoped approvals, explicit data-source whitelist, and local Control Plane events as the first automation surface.

## Email Sending

Goal:

- send 08:00 daily plan emails
- send 22:00 daily snapshot emails
- send weekly and monthly report emails

Required decisions:

- sender account
- recipient list
- authentication mechanism
- dry-run mode
- retry policy
- sent confirmation source
- redaction rules

## Email Reply Feedback

Goal:

- ingest replies as feedback records

Required decisions:

- mailbox connector
- allowed folders or labels
- retention policy
- conflict handling with Codex and journal feedback

## Scheduler

Goal:

- run report generation and email sending on schedule

Required decisions:

- cron, systemd timer, or dedicated service
- timezone handling
- missed-run behavior
- manual override command

## Data Connectors

Potential future sources:

- calendar
- browser or research history
- chat or IM
- health and exercise exports
- cloud drive docs

Every connector requires explicit whitelist approval before use.

## Automation Acceptance Criteria

- no non-whitelisted source enters a report
- emails are generated with source references
- failed sends do not mark `sent_at`
- 22:00 late-work rule is preserved
- feedback can update low-risk templates and route high-risk changes to approval
