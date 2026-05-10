---
artifact_type: issue
title: source refs context resolver
status: needs-triage
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0014-llm-drafting-in-runtime-v1.md
  - ../../../docs/adr/0015-runtime-v1-1-controlled-context-expansion.md
  - ../../../docs/runtime-v1-tdd-hardening.md
confidence: medium
approval_state: draft
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: source refs context resolver

## Parent

`../PRD.md`

## What To Build

Add a bounded resolver that turns a parent artifact's explicit `source_refs` into an auditable context pack for `paos draft <parent>`. The resolver should include allowed repo-local docs or code snippets and record excluded references before any LLM provider call.

## Acceptance Criteria

- [ ] Reads `source_refs` from parent frontmatter.
- [ ] Resolves relative paths from the parent artifact directory.
- [ ] Supports explicit repo-root-relative references when the syntax is defined in the implementation plan.
- [ ] Includes only allowed repo-local files under approved roots.
- [ ] Rejects Private Runtime Log paths, private config paths, `.git` internals, credential-looking files, and unapproved external URLs by default.
- [ ] Records included refs with path, kind, byte count or truncation, reason, and source field.
- [ ] Records excluded refs with exclusion reason.
- [ ] Adds behavior tests before implementation: one allowed local ref, one blocked private log ref, and one blocked out-of-root ref.

## Implementation Notes

Do not replace the current default exclusion boundary from Runtime v1. The resolver expands context only from explicit refs and must run before `LLMClient.DraftRuntimeTask` is called.

## Test Plan

- RED: focused test for allowed `source_refs` appearing in the rendered LLM Payload.
- RED: focused test for blocked Private Runtime Log contents not being read.
- RED: focused test for path traversal or out-of-root refs being excluded.
- GREEN: implement minimum resolver and payload rendering changes.
- REFACTOR: keep resolver as a testable module independent of provider HTTP calls.

## Risks

- Path handling is security-sensitive. Treat ambiguous paths as excluded until an approved design says otherwise.

## Comments

Append discussion and triage notes here.
