---
artifact_type: feedback_record
date: 2026-05-29
timezone: Asia/Shanghai
source_refs:
  - current Codex conversation on 2026-05-29: user compared secureBody explanation styles and requested a brain-science-based workflow improvement
  - workflows/self-improvement.md
  - system/risk-and-hitl-policy.md
  - workflows/engineering-delivery.md
  - /tmp/communication-cognitive-load.json
  - /tmp/communication-primary-cognitive-sources.json
  - /tmp/communication-cognitive-efficiency.md
  - https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/magical-number-4-in-shortterm-memory-a-reconsideration-of-mental-storage-capacity/44023F1147D4A1D44BDC0AD226838496
  - https://www.nngroup.com/articles/progressive-disclosure/
  - https://education.nsw.gov.au/content/dam/main-education/about-us/educational-data/cese/2017-cognitive-load-theory.pdf
confidence: high
approval_state: applied
risk_level: low
sent_at: null
late_supplement_for: null
feedback_source: Codex conversation
target_artifact: workflows/engineering-delivery.md
---

# Feedback Record: 2026-05-29

## Feedback

The user pointed out that this style was easier to understand:

1. Frontend generates an AES-GCM symmetric key and uses it to encrypt the original body.
2. Frontend gets the backend RSA public key and uses it to encrypt that AES-GCM key.
3. Frontend puts the encrypted body, encrypted key, nonce, and copied metadata into `secureBody`.

The user contrasted that with a more field-heavy explanation that started from endpoint fetch, JWK import, intermediate variable names, and final JSON fields. The user's version was easier for colleagues because it compressed the protocol into three meaningful operations before introducing the field mapping.

## Source Channel

Codex conversation feedback.

## Target

`workflows/engineering-delivery.md`, especially technical explanations, API docs, security protocol docs, architecture explanations, and handoffs.

## Classification

Low-risk.

Reason: this changes wording and checklist guidance only. It does not add data sources, lower HITL gates, change role responsibility, change automatic email policy, change Git or remote policy, or increase execution autonomy.

## Research Basis

The change is grounded in cognitive-load and documentation-structure evidence:

- Working memory capacity is limited; Cowan's review argues that pure short-term memory capacity is closer to about four chunks than an unlimited stream of items.
- Cognitive load theory treats presentation format as part of extraneous load; reducing avoidable presentation complexity preserves capacity for understanding.
- Schema theory explains why a meaningful high-level chunk can behave like one working-memory element even when it contains many low-level details.
- Progressive disclosure keeps advanced or detailed information available while presenting the minimal current task first.

## Proposed Change

Add a communication-efficiency rule:

- first provide a one-sentence mental model
- then explain the core flow in 2-4 semantic chunks
- only after that map the chunks to exact fields, endpoints, files, commands, edge cases, and code
- keep the first-pass flow restatable in three bullets or fewer

## Action Taken

- Auto-applied: added `Communication Efficiency` to `workflows/engineering-delivery.md`.
- Auto-applied: clarified that Codex conversation feedback records live under `.scratch/self-improvement/feedback/`.
- Auto-applied: added "clearer first-pass mental models before exhaustive reference detail" to the self-improvement quality bar.
- Needs approval: none.

## Result Check

Future agent explanations should be easier to restate from memory. A quick review check is: can the user restate the core process in three bullets before reading the field table?
