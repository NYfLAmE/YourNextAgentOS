# Runtime v1 Self-Test

This document records the local self-test boundary for the first `paos` implementation. It is intentionally local-only and does not require Telegram, email, calendar, browser history, or other external connectors.

## Scope

The implemented self-test covers:

- private config discovery without printing secret values
- read-only `.scratch/**.md` Control Plane scanning
- LLM Drafting through an OpenAI-compatible mock provider
- strict JSON Runtime Task Draft validation
- Approval Record creation and Runtime Task state transition to `ready`
- approved Command List execution in a dedicated Git worktree
- Private Runtime Log writes outside the Git-backed Control Plane
- failed Runtime Task repair payload construction without reading full Private Runtime Log contents

## Automated Check

Run from the repository root:

```bash
go test ./...
```

The test suite uses temporary directories, a mock LLM provider, and a temporary Git repository. It does not require a real API key and does not write Private Runtime Logs into this repository.

## Manual Smoke Checks

These commands are read-only unless `approve`, `run`, or `draft` is used against a real Runtime Task:

```bash
go run ./cmd/paos --root /home/ZykLyj/yjdev/personal-agent-os status
go run ./cmd/paos --root /home/ZykLyj/yjdev/personal-agent-os scan
go run ./cmd/paos --root /home/ZykLyj/yjdev/personal-agent-os watch --once
```

`paos draft <parent>` requires private local config at `~/.personal-agent-os/config.yaml` or an explicit `--config <path>`:

```yaml
runtime_dir: /home/ZykLyj/.personal-agent-os/runtime
worktree_root: /home/ZykLyj/.personal-agent-os/runtime/worktrees
llm:
  base_url: https://example-openai-compatible-provider/v1
  model: example-model
  api_key_env: PAOS_LLM_API_KEY
```

Do not commit this private config or API key values.

## Evidence Boundary

Runtime Task Markdown may reference Private Runtime Log paths, but it must not paste full stdout, stderr, or secrets into the Git-backed Control Plane. Full command output belongs in the private runtime directory configured outside Git.
