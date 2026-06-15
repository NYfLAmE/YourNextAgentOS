---
name: route-decision-research
description: Build source-backed product or technical route-decision research packs from local evidence, public sources, capability maps, and optional throwaway prototypes. Use when the user asks to compare implementation routes, define a 30/60/90 day MVP path, evaluate agent/framework/product architecture choices, or turn messy research into a decision report.
---

# Route Decision Research

Use this skill to turn an ambiguous product or technical direction into a decision-ready research pack. It orchestrates evidence gathering and synthesis; it does not replace narrower skills like `parallel-web-search`, `parallel-deep-research`, `prototype`, or repo-specific onboarding skills.

## Trigger Check

Use when the task has all of these:

- a concrete decision horizon, such as an MVP, route choice, architecture direction, or executive recommendation
- local evidence to inspect, such as repos, docs, prototypes, existing plugins, or prior notes
- external context to compare against, such as market products, frameworks, official docs, or competitor patterns
- a need for a durable artifact, not just a quick chat answer

Skip or use another skill when the task is only bug diagnosis, pure web lookup, pure prototype building, or a one-file code change.

## Evidence Ladder

Prefer evidence in this order:

1. User-provided brief, current conversation, and explicit constraints.
2. Local source repos, sidecar analysis docs, existing prototypes, package contents, runtime files, and command output.
3. Official docs and first-party public sources.
4. Reputable third-party sources for market/product context.
5. Deep research outputs only when the user explicitly asked for deep or exhaustive research.

Keep facts separate from inference using labels such as `Fact`, `Decision`, `Risk`, `Constraint`, `Assumption`, and `Open Question`.

## Standard Artifacts

Create or update a sidecar research directory when the work is more than a chat answer. A typical pack is:

```text
00-source-log.md
01-local-baseline.md
02-market-and-framework-research.md
03-capability-map.md
04-route-decision-report.md
prototypes/<question-slug>/NOTES.md
```

Adapt names to the domain, but keep the sequence: source trail, local baseline, external comparison, capability/risk map, final route decision. Use a sidecar workspace for mirror repos or read-only sources.

## Workflow

1. State the decision question, time horizon, audience, and non-goals.
2. Build a source log as you inspect evidence. Record local paths, command types, URLs, remote read-only scope, and excluded/noisy sources.
3. Establish the local baseline before comparing external options: current architecture, capability surface, security model, gaps, and reusable assets.
4. Use `parallel-web-search` for current public context. Use `parallel-deep-research` only when explicitly requested. For OpenAI product/API facts, use the OpenAI docs skill and official docs.
5. Convert local capabilities into a map: domain, supported actions, missing actions, risk level, required permissions, confirmation needs, post-checks, and audit expectations.
6. Compare routes by what each can do, cannot do, cost, team fit, security risks, and long-term migration risk.
7. If the main uncertainty is UX or state behavior, invoke `prototype` and capture the question, variants, run command, and review decisions in `NOTES.md`.
8. Write the route decision report with an answer-first recommendation, rejected options, 30/60/90 day MVP split, architecture sketch, key risks, and open questions.
9. Verify that every important claim has a source reference or is labeled as an assumption.

## Quality Bar

- Do not present a demo repo, vendor framework, or agent runtime as production-ready without evidence.
- Do not let public market claims override local permission, deployment, auth, audit, or team constraints.
- Preserve read-only boundaries for mirrors and remote systems unless the user explicitly changes scope.
- Keep credentials and secret values out of artifacts; record only the access method and read/write boundary.
- Recommend the smallest route that proves the decision horizon. Put broader platform ambitions into later phases or open questions.

## Done

The task is done when the user has:

- a clear recommended route and why it wins
- a source log that lets another agent audit the evidence chain
- a local baseline and external comparison that separate facts from judgment
- a capability/risk map tied to MVP scope
- optional prototype notes that say what question the prototype answers
- explicit skipped routes and open questions
