---
artifact_type: issue
title: paos CLI skeleton and private LLM config
status: needs-triage
category: enhancement
source_refs:
  - ../PRD.md
  - ../../../CONTEXT.md
  - ../../../docs/adr/0004-go-single-binary-runtime.md
  - ../../../docs/adr/0012-paos-cli-name.md
  - ../../../docs/adr/0014-llm-drafting-in-runtime-v1.md
confidence: medium
approval_state: draft
risk_level: high
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Issue: paos CLI skeleton and private LLM config

## Parent

`../PRD.md`

## What To Build

Create the first `paos` Go CLI skeleton and private local configuration loading for Runtime v1. This slice should establish the binary name, command dispatch, config path default, and OpenAI-compatible LLM config shape without implementing LLM calls yet.

## Acceptance Criteria

- [ ] `paos` has commands for `watch`, `scan`, `draft`, `approve`, `run`, and `status`, even if later commands return clear "not implemented" messages.
- [ ] The default private config path is `~/.personal-agent-os/config.yaml`.
- [ ] The LLM config shape supports `base_url`, `model`, and `api_key_env`.
- [ ] `paos status` can report config discovery without printing secret values.
- [ ] No private config or API key is written into the Git-backed Control Plane.

## Blocked By

None - can start immediately.

## Implementation Notes

Respect ADR-0012 for the CLI name and ADR-0014 for private LLM config boundaries. This issue should not call a model provider.

## Test Plan

- Unit test config loading with a temp config file.
- Unit test missing config behavior.
- Run the repo's Go tests after the Go module exists.

## Risks

- Accidentally logging `api_key_env` values or resolved secrets would violate the private config boundary.

## Comments

Append discussion and triage notes here.
