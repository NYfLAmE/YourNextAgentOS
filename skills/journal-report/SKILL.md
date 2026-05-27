---
name: journal-report
description: Generate, backfill, or roll up Personal Agent Journal daily, weekly, monthly, and email-draft report artifacts from whitelisted evidence. Use when the user asks for a daily report, weekly report, monthly report, work report, report backfill, late supplement, journal update, or report email draft.
---

# Journal Report

Create private work-report artifacts in:

```text
/home/ZykLyj/yjdev/personal-agent-journal/
```

Use this as a thin execution skill over the canonical Personal Agent OS reporting rules, not as a replacement for those rules.

## Required Context

1. Read `/home/ZykLyj/yjdev/personal-agent-os/README.md`.
2. Read `/home/ZykLyj/yjdev/personal-agent-os/workflows/reporting-and-planning.md`.
3. Read `/home/ZykLyj/yjdev/personal-agent-os/data-sources/whitelist.md`.
4. Read the matching journal README:
   - `personal-agent-journal/reports/daily/README.md`
   - `personal-agent-journal/reports/weekly/README.md`
   - `personal-agent-journal/reports/monthly/README.md`, when present
   - `personal-agent-journal/email-drafts/README.md`, for email drafts
5. If the report covers Terra/OpenClaw work, also use `terra-onboarding` before summarizing project facts.

## Evidence Rules

- Use only whitelisted sources: Codex sessions, Codex memories and rollout summaries, local Git metadata, current conversation, journal repository files, and project files explicitly in scope.
- Prefer current source files, command output, and Git metadata over stale memory when the claim affects a current decision.
- Do not use mailbox, calendar, browser history, chat history, cloud drive, health data, financial data, or system-wide activity logs unless the whitelist has been explicitly updated.
- Do not quote or persist secrets, tokens, cookies, API keys, private keys, or raw credentials.
- Treat journal content as private; do not copy private report prose into public project docs.

## Workflow

1. Determine artifact type and date range.
   - Daily reports use Asia/Shanghai natural dates.
   - Weekly reports use `YYYY-Www`.
   - If the user says "yesterday", "today", or "this week", resolve it to concrete dates in Asia/Shanghai.
2. Inspect existing target files before writing.
   - Daily path: `reports/daily/YYYY/MM/YYYY-MM-DD.md`.
   - Weekly path: `reports/weekly/YYYY/YYYY-Www.md`.
   - Monthly path: `reports/monthly/YYYY/YYYY-MM.md`.
3. Gather evidence in source order.
   - Recent Codex sessions for the target dates.
   - MEMORY.md and rollout summaries for completed-task cross-checks.
   - Existing daily reports when creating weekly or monthly rollups.
   - Git log/status/diff metadata for named repos.
   - Project files only when the project is explicitly in scope.
4. Write the artifact from the matching Personal Agent OS template.
   - Include `source_refs`.
   - Set `confidence` based on evidence completeness.
   - Keep `approval_state: draft`.
   - Keep `sent_at: null` unless a send was explicitly confirmed.
5. Preserve the 22:00 snapshot rule.
   - Work after 22:00 and before local midnight stays attached to the same natural date.
   - Add a late supplement instead of moving it to the next day's accomplishments.
6. Validate and report.
   - Run `git diff --check -- <changed-files>`.
   - Check `git status --short` in the journal repo.
   - State changed files, evidence limits, and any missing dates or blocked sources.

## Output Bar

- Reports must be factual, source-backed, and suitable for later weekly or monthly rollup.
- Weekly and monthly reports may summarize daily facts but must not invent achievements missing from whitelisted evidence.
- Review sections should contain 1 to 3 concrete experiments, not generic motivation.
- Email work creates drafts only; do not send email unless a separate approved sending workflow exists.
