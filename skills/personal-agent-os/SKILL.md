---
name: personal-agent-os
description: Route Codex into the user's lightweight Personal Agent OS by reading the canonical local handbook instead of embedding its contents. Use when the user invokes /personal-agent-os, $personal-agent-os, personal-agent-os, Personal Agent OS, 个人 agent OS, 个人agent系统, or asks to run work through their personal agent OS.
---

# Personal Agent OS

## Source of truth

This skill is only an entry point. The canonical operating system lives at:

```text
/home/ZykLyj/yjdev/personal-agent-os/
```

Do not duplicate or override that repository's rules in this skill. When this skill is loaded, read the OS files needed for the current task and treat current file contents as authoritative.

## Required first step

Always read:

```text
/home/ZykLyj/yjdev/personal-agent-os/README.md
```

Then follow its links according to the task:

- Role selection or handoff: `system/agent-roster.md` and `system/shared-context-contract.md`
- Approval, autonomy, side effects, credentials, email, or policy changes: `system/risk-and-hitl-policy.md`
- Engineering requirements, bugs, PRDs, issues, implementation, review, docs, commit, or push: `workflows/engineering-delivery.md`
- Daily, weekly, monthly, planning, report, late supplement, or email-draft work: `workflows/reporting-and-planning.md`
- Feedback, template refinement, or workflow improvement: `workflows/self-improvement.md`
- Evidence gathering for reports or plans: `data-sources/whitelist.md`
- Terra/OpenClaw backend work: `projects/terra-openclaw-setup-backend.md`

## Operating rules

- Use the OS as routing and governance, not as a replacement for current repo facts, command output, or user instructions.
- For factual claims, cite source files, command output, journal entries, memory files, or explicit user statements as required by the OS.
- If OS rules conflict with current files or the user's newest instruction, apply the OS conflict-resolution policy after reading the relevant file.
- Keep responses in Chinese by default unless the active task or user instruction calls for another language.
