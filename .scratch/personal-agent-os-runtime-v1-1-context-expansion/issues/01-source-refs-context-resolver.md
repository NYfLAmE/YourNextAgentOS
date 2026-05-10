---
artifact_type: issue
title: source refs context resolver
status: ready-for-human
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0014-llm-drafting-in-runtime-v1.md
  - ../../../docs/adr/0015-runtime-v1-1-controlled-context-expansion.md
  - ../../../docs/runtime-v1-tdd-hardening.md
confidence: medium
approval_state: approved
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

Add a bounded resolver that turns a parent artifact's explicit frontmatter `source_refs` into an auditable context pack for `paos draft <parent>`. The resolver should include allowed local text references in the LLM Payload and record excluded references before any LLM provider call.

## Acceptance Criteria

- [x] Reads `source_refs` from parent frontmatter only.
- [x] Resolves relative paths from the parent artifact directory.
- [x] Allows explicit absolute paths when they are listed in `source_refs`.
- [x] Includes allowed local text files in the LLM Payload.
- [x] Rejects Private Runtime Log paths, PAOS private config paths, `.git` internals, credential-shaped files, binary/non-UTF-8 files, and unapproved external URLs by default.
- [x] Truncates included content at 64KB per file with no global total-size limit.
- [x] Records included refs with full absolute path, byte count, truncation state, reason, and source field.
- [x] Records excluded refs with full absolute path and exclusion reason.
- [x] Writes Runtime Task Draft Context Pack metadata only, not included file contents.
- [x] Adds behavior tests for allowed relative refs, explicit absolute refs, sensitive refs, large refs, and binary refs.

## Implementation Notes

Do not replace the current default exclusion boundary from Runtime v1. The resolver expands context only from explicit frontmatter refs and must run before `LLMClient.DraftRuntimeTask` is called. Plain `source_refs` are not credential-reading authorization; any future support for credential-shaped files requires a separate high-risk ADR.

## Test Plan

- RED/GREEN: allowed `source_refs` content appears in the rendered LLM Payload while Runtime Task Draft persists metadata only.
- RED/GREEN: Private Runtime Log, PAOS private config, `.git`, and credential-shaped refs are excluded without reading contents.
- RED/GREEN: external URL refs are excluded without network access.
- GREEN characterization: explicit absolute text refs are allowed.
- GREEN characterization: large refs are truncated at 64KB and marked `truncated=true`.
- RED/GREEN: binary/non-UTF-8 refs are excluded with a stable reason.
- REFACTOR: keep resolver as a testable module independent of provider HTTP calls.

## Risks

- Path handling is security-sensitive. Treat ambiguous paths as excluded until an approved design says otherwise.

## Comments

Append discussion and triage notes here.

Implementation note 2026-05-10:

- Implemented `source_refs` Context Pack resolution for `paos draft`.
- Runtime Task Drafts now include a `## Context Pack` metadata section with full absolute paths, included/excluded status, source field, byte count, truncation state, and reason.
- LLM Payload includes included text file content, capped at 64KB per file, and excludes sensitive or binary refs.
- This slice intentionally does not implement project adapters, TDD-aware DraftResponse schema changes, or watcher-assisted drafting.
