---
name: adk-go-skill
description: Bootstrap factual onboarding and architecture comparison for the local google/adk-go repository. Use when analyzing ADK-Go, Google Agent Development Kit for Go, Go agent runtime design, or comparing ADK-Go with Terai, pi, or OpenClaw architecture.
---

# ADK-Go Skill

## Purpose

Use this skill to analyze the local `/home/ZykLyj/yjdev/adk-go` repository and map its agent runtime design to Terai architecture decisions. It is a routing and evidence skill, not a replacement for current source verification.

## Quick Start

1. Default repo: `/home/ZykLyj/yjdev/adk-go`.
2. Default sidecar: `/home/ZykLyj/yjdev/adk-go-sidebar`.
3. Check current source state first:

```bash
git status --short --branch
git log -1 --oneline
```

4. Read sidecar entrypoints in this order:
   - `/home/ZykLyj/yjdev/adk-go-sidebar/INDEX.md`
   - `/home/ZykLyj/yjdev/adk-go-sidebar/01-adk-go-architecture-map.md`
   - `/home/ZykLyj/yjdev/adk-go-sidebar/02-terai-fit-comparison.md`

5. Then read task-specific source files.

## Source Routes

- Overview: `README.md`
- Agent interface: `agent/agent.go`
- Runner: `runner/runner.go`
- Session and Event: `session/session.go`, `session/service.go`
- LLM agent config: `agent/llmagent/llmagent.go`
- LLM flow internals: `internal/llminternal/base_flow.go`
- Model interface: `model/llm.go`, `model/gemini/gemini.go`
- Tools: `tool/tool.go`, `tool/functiontool/function.go`
- Skills: `tool/skilltoolset/toolset.go`, `tool/skilltoolset/skill/`
- MCP: `tool/mcptoolset/`, `examples/mcp/main.go`
- Plugins/callbacks: `plugin/plugin.go`, `internal/plugininternal/`
- Workflow agents: `agent/workflowagents/`
- A2A/remote agents: `agent/remoteagent/v2/`, `server/adka2a/`
- REST/SSE: `server/adkrest/`

## Terai Comparison Rules

- Treat ADK-Go as an agent runtime toolkit, not a Terai Host Kernel.
- Do not treat `userID/appName/sessionID` as OS-level multi-user isolation.
- Do not treat `plugin.Plugin` as OpenClaw manifest plugin runtime; it is an in-process Go callback API.
- Do not treat `SkillToolset` as Terai skill/plugin installation and permission semantics; use it only as a progressive disclosure reference.
- Do not use ADK-Go `model.LLM` as the final Terai provider design; Terai still needs ProviderRegistry, ModelCapability, admin model center, credential scope, quota, policy, and fallback.
- If comparing with Terai, also read `/home/ZykLyj/yjdev/tafs_sidebar/13-terai-clean-architecture-route-decision.md`.

## Useful Validation

Representative package test:

```bash
go test ./agent/... ./runner ./session/... ./tool/... ./model/... ./plugin/... ./memory/... ./artifact/... ./server/adkrest/... ./server/agentengine/...
```

Do not run examples that need external API keys unless the user explicitly asks and provides a safe credential path.

## Output Style

When answering architecture questions, separate:

- `Fact`: current source, docs, or command output.
- `Inference`: reasoned interpretation from facts.
- `Recommendation`: what Terai should borrow or avoid.
- `Open Question`: what still needs a spike or current-source check.
