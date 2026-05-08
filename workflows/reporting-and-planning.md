# Reporting And Planning Workflow

This workflow generates work-focused daily, weekly, and monthly artifacts.

## Scope

V1 focuses on work content. Life and health sections are reserved for future data sources and must not include unsupported judgments.

## Time Rules

Timezone: Asia/Shanghai.

Default schedule:

- 08:00: daily plan email draft
- 22:00: daily report snapshot email draft
- Friday 22:00: weekly report draft
- last workday 22:00: monthly report draft

V1 creates drafts and archives. V2 may automate sending.

## 22:00 Snapshot And Late Work

The 22:00 report is a snapshot of known facts at that time.

If work continues after 22:00:

- keep attributing the work to the same natural date until local midnight
- append it to that date's daily report as a late supplement
- include a "昨日晚间补充" section in the next 08:00 plan
- do not move late work into the next day's accomplishments

## Allowed Fact Sources

Reporter may only use sources listed in [data source whitelist](../data-sources/whitelist.md).

If a potentially useful source is not whitelisted:

- do not summarize it
- mention that it is unavailable as a source
- propose adding it to the whitelist only when the benefit is concrete

## Daily Plan

Use the daily template in [daily-report.md](../templates/daily-report.md) with `artifact_type: daily_plan` or a separate dated section.

Required sections:

- yesterday late supplement if present
- today's confirmed commitments
- recommended focus order
- risks or blockers
- decisions needed from the user

## Daily Report

Required sections:

- factual work completed
- work in progress
- decisions made
- evidence/source references
- blockers
- tomorrow proposal
- review and improvement experiments
- late supplement section when applicable

Review style: evidence plus small experiments. Provide 1 to 3 concrete experiments, not generic motivation.

## Weekly Report

Use [weekly report template](../templates/weekly-report.md).

Required sections:

- weekly outcomes
- progress by project
- repeated blockers
- quality and workflow observations
- next week proposal
- review and improvement experiments

Weekly reports may reuse daily facts but must not invent achievements missing from daily evidence.

## Monthly Report

Use [monthly report template](../templates/monthly-report.md).

Required sections:

- monthly outcomes
- performance evidence
- project impact
- capability growth
- unresolved risks
- next month proposal
- review and improvement experiments

Monthly reports should be suitable as a basis for performance review, but claims must remain evidence-backed.

## Email Draft Rules

V1 creates email drafts under the journal repository. It does not send.

Draft metadata must include:

- `sent_at: null` until actual sending exists
- intended send time
- recipient placeholder
- source references
- whether the draft is a snapshot or final rollup

V2 email automation must preserve these fields and update `sent_at` only after successful send confirmation.
