---
name: terai-onboarding
description: Bootstrap factual onboarding and task execution for the Terai product and tafs technical base. Use when working on Terai, tafs/Terai architecture, tos-agentd, Terai requirements, Terai beta planning, terai_ye demo comparison, or when user says terai-onboarding, Terai 项目上手, 项目上下文, or wants a fresh agent/GPT to answer or implement Terai-related work.
---

# Terai Onboarding

## Purpose

Use this skill as the compact replacement for long Terai onboarding prompts. It is a bootstrap router and guardrail, not a fact boundary: current repo files, command output, tests, latest meeting records, and explicit user instructions win.

Terai is the product/project name. `tafs` is the high-confidence technical base that will evolve toward the formal framework. `terai_ye` is a demo/reference only; do not treat its Python shim or UI choices as the formal architecture unless current Terai facts or source verification explicitly say so.

## Quick Start

1. Default workspace: `/home/ZykLyj/yjdev`.
2. Run the helper to list the current context pack:

```bash
/home/ZykLyj/.agents/skills/terai-onboarding/scripts/context-pack.sh "<user task summary>"
```

3. Read every `[required]` file.
4. Read `[latest-meeting]` records when the task touches product direction, scope, planning, or decisions.
5. Read `[current]` facts and analysis before older summaries.
6. Read `[source]` and `[route]` files that match the task.
7. Continue following links, code, tests, scripts, sidebars, and sibling repos discovered from those files. The helper never limits the fact surface.
8. Before conclusions, separate `Fact`, `Assumption`, `Decision`, `Risk`, and `Open Question`.

## Fact Priority

When facts conflict, use this order:

1. Current user instruction.
2. Current `tafs` source, command output, tests, and deployed `tos-agentd` behavior.
3. Latest Terai meeting records and `tafs_sidebar/11-terai-current-facts.md`.
4. `tafs_sidebar` source analysis.
5. `terai_ye` source and `terai_ye_sidebar` analysis as demo/reference.
6. Older meeting analysis, memory, or chat context.

Do not infer formal backend architecture from `terai_ye`. Use it for UI/product-demo ideas, packaging clues, API-shape comparison, and migration input only.

## Sidebar Sync Rules

- Treat `/home/ZykLyj/yjdev/tafs_sidebar` as the durable sidecar for Terai architecture, source analysis, meeting-derived decisions, route decisions, and recurring bug/risk findings.
- When a Terai discussion produces a new decision, supersedes an older conclusion, or changes the recommended route, update the matching `tafs_sidebar` document in the same turn when the user asks to preserve or sync the conclusion.
- If an answer relies on an older `tafs_sidebar` conclusion that current source or current user instruction supersedes, update the sidecar or explicitly say why no update was made.
- For current-source `tafs` analysis, use a write-through rule: if the analysis produces a new behavior fact, architecture conclusion, bug/risk, or supersedes an older conclusion, update the closest `tafs_sidebar` document in the same turn by default. If no durable update is needed, say why.
- Prefer updating existing canonical files first: `11-terai-current-facts.md` for current facts, route-decision docs for architectural direction, module notes for source-level findings, and `INDEX.md` for discovery/routing.
- Add a new sidebar document only when the conclusion spans multiple existing docs or needs a stable decision record of its own.
- Do not update `tafs_sidebar` for every casual thought; update it for decisions, current-source facts, repeated diagnosis findings, architecture direction, and work rules that future agents or teammates should reuse.
- Sidecar updates are documentation changes and are allowed when the user explicitly asks to write/update docs or preserve a conclusion. They still require source-backed wording and a docs-sync note in the final response.

## Architecture Writing Rules

- For Terai architecture docs, prefer Chinese explanatory names first, with English identifiers in backticks only when they help map to code or future interfaces.
- Avoid relying on abstract English terms alone. If a term like `materialize`, `surface`, `binding`, `snapshot`, `provider-visible`, or `executor registry` appears, explain it in plain Chinese nearby.
- Preferred wording examples:
  - `materialize` -> `生成本次运行快照`
  - `AgentSurfaceSnapshot` -> `本次 Agent 可见能力快照`
  - `provider-visible tool definitions` -> `模型/API 可见的工具定义`
  - `hidden executor registry` -> `后端执行器映射，模型不可见`
  - `surface binding` -> `能力如何投射到用户界面或 Agent 可见能力`
- For supervisor-facing or teammate-facing explanations, answer “这个模块为什么存在、解决什么问题、运行时发生什么” before listing interface names.
- 先场景后术语（2026-06-24 用户反馈强化）：向人解释任何概念、设计、机制或选项前，先用一两句白话说清“这是什么业务场景下的什么问题、不做会怎样”，再说做法，最后才给接口名/字段/标识符。每个英文或专有术语（如 `flat threshold`、`pair-safe`、`cooldown`、`snapshot`）首次出现必须就地用中文解释；不要一次抛出多个未解释的术语——宁可多一句场景，也不要多一个生词。
- Keep architecture writing source-backed and precise, but do not make the wording more bookish than necessary.

## Module Design & Decomposition Rules（模块设计与拆分规范）

> 2026-06-25 用户定夺。适用于 Terai/`tafs` 所有模块的设计、拆分、命名与评审，用于终结“模块怎么切、职责归谁”的反复扯皮。每条附 Terai 现状示例，便于他人据现状直接判断。

- 目标优先于方法：架构目标永远是四属性——`合理分层`、`合理拆分`、`职责清晰`、`低耦合高内聚`。DDD/Clean/hexagonal 都是手段、不是验收标准；为套方法而引入复杂度（over-engineering）本身就是反模式。
  - 例：`模型供应`(Provider) 只是把消息转给 OpenAI/Claude 再转回统一格式的适配层，给它套 `aggregate`/`repository` 是过度设计。判断标准是“这样切是否更清晰、更低耦合”，不是“是否更像 DDD 教科书”。
- DDD 战略广泛用：每个模块都做“切块 + 正向命名 + 边界清楚 + 统一语言”（限界上下文 `bounded context`、子域 `subdomain`、统一语言 `ubiquitous language`）。这层成本低、收益高,是“合理拆分 + 职责清晰 + 低耦合”的主要来源。
  - 例：即便是技术模块 `可观测`(Observability)，也要正向命名、边界清楚（correlation/日志/trace/metrics 各司其职），而不是叫 `utils` 或塞进 `common`。
- DDD 战术只在真领域用：重型对象建模（聚合 `aggregate`、值对象 `value object`、仓储 `repository`、领域服务 `domain service`）只用于“有复杂业务规则、有边界条件、会被反复争论”的真领域。（如 `会话与上下文`：分支/fork/锚点/上下文选择）。纯技术或横切机制（如 `模型供应` 调 provider、`提示词组装` 拼字符串、`可观测` 写日志）按普通整洁代码 + ports/adapters 写，不硬上战术 DDD。
  - 例（该上）：`会话与上下文` 里“改历史输入不能原地改、要新建 `branch`，从某条 assistant 消息续接要定位 `ContextAnchor`”是有规则的，值得用聚合统一保证分支一致性。
  - 例（别上）：`提示词组装` 只是把 `ContextPackage` 渲染成字符串，没有规则可争，写成普通 pipeline/函数即可。
- 真领域 vs 技术机制：判一个模块属哪类，看“它有没有业务规则可争”。有 → 真领域，可上战术；只是搬运/适配/横切 → 技术机制，只守通用设计律。
  - 例：真领域＝approval 审批闭环（什么状态能批/拒/超时、能否恢复）；技术机制＝把 SSE 六事件透传给前端、把 plugin manifest 转成 tool。
- 正向命名，禁否定式/技术分层命名：模块按“它是什么 / 负责哪个领域”命名；禁止按“不是什么”（catch-all 大筐）或纯技术分层（`controllers`/`services`/`util`/`common`）命名。说不清一句话职责、或要靠排除法定义的，一律视为拆分嫌疑。
  - 例（反）：`non-capability`＝“除了能力剩下的全归我”，说不清职责。
  - 例（正）：把它原想装的东西按领域拆回各正主——LLM profile 配置回 `模型供应`、policy 配置回 `运行治理`、session 列表回 `会话与上下文`。
- 横切关注点不必是子域：治理、可观测、暴露/投递、提示词渲染等横切机制可做成横切层（interceptor/adapter/advisor 风格），不要为“凑成 bounded context”硬塞成业务子域。
  - 例：`Agent 工具调用` 是把能力暴露给模型的 driving adapter（与 REST controller 平级），不是一个拥有功能的子域，不是“拥有搜索逻辑的子域”；搜索的索引/查询/配置应高内聚在“搜索”这块，不被“是否被 agent 调用”劈成两半。
- 模块拆分判定清单（litmus，任一条“否”即拆分嫌疑）：
  1. 一句话能说清它是什么吗？（不带“和/或”、不靠否定）
  2. 它因“同一类原因”才变更吗？（共同闭包原则 `CCP`）
  3. 一个典型功能改动是否只动一个模块？（低耦合、未被劈裂）
  4. 是否按领域/职责正向命名，而非“不是什么”或技术分层？
  5. 对外是深接口（小接口、藏复杂度），还是把复杂度甩给调用方？
  6. 它是真领域（可上战术 DDD），还是技术/横切机制（只守通用设计律）？
  - 套用示例（反例 `non-capability`）：①否——只能说“剩下的”；②否——session/provider/policy 因不同原因变更；④否——否定式命名。三条挂 → 必拆。
  - 套用示例（正例 `会话与上下文`）：①是——“管会话视角与本轮上下文”；②是——都因会话/上下文规则变更；③是——改分支逻辑只动这块；全过 → 合理。
- 评审落点：模块设计/拆分结论进 per-module ADR 与 `tafs_sidebar`（架构方向进 `18`，当前事实进 `11`）。与既有规则配合：`Architecture Concept Introduction Rules`（控制新增概念）+ `Architecture Reference Research Rules`（先调研成熟参考）+ 本规范（怎么切 / 怎么命名 / 怎么判）。

## Architecture Concept Introduction Rules

When discussing or documenting Terai architecture, do not introduce a new concept, module, struct, field, event, or identifier just because another agent framework uses it.

Before a new architecture concept enters a target architecture doc or interface proposal, answer these checks:

- What concrete product or engineering scenario requires it?
- Why can existing Terai concepts not carry that responsibility?
- Which module owns it, who creates it, who consumes it, and who persists it?
- Is it part of V1, or only a V2+ candidate?
- Can the name be simpler or explained with a Chinese descriptive term first?
- Does it introduce migration, privacy, audit, storage, UI, or evaluation complexity?
- If it is only a future capability, can the current design use a lighter anchor/ref instead of a full snapshot/store/schema?

If a concept does not pass this necessity check, keep it out of the target architecture and record it only as an open question or future candidate.

## Architecture Reference Research Rules

For Terai architecture-level discussions, before the next analysis, grill, or decision step, first delegate focused sub-agents to research mature agent products, frameworks, or architecture references when such references can reasonably inform the question.

Use this rule for module boundaries, naming, data flow, state machines, context / memory / prompt, runtime, capability, provider, observability, approval, security policy, and other target-architecture decisions.

Each delegated research result must be traceable and must separate `Fact`, `Inference`, and `Recommendation`. It should include local source paths or document paths, line numbers or stable anchors where available, and an explicit mapping back to the relevant Terai modules.

Do not use this rule for pure current-source fact lookup, obvious small wording edits, user instructions that explicitly skip external/reference research, or cases where no mature reference source is available. If this rule is skipped for an architecture topic, state why.

## Task Routing

- Product requirement / new feature track: `terai-onboarding -> grill-with-docs -> to-prd -> to-issues -> triage -> tdd`. Use this for fuzzy product needs, user-facing features, scope discussions, or multi-agent/task-tracker coordination.
- Architecture refactor / module split track: `terai-onboarding -> grill-with-docs -> per-module ADR/opening brief -> approval -> tdd/behavior lock -> R/S-separated implementation -> review -> docs sync`. Use this for Terai architecture boundaries, module extraction, or `tafs` refactors toward `18-terai-target-architecture-task-record-2026-06-18.md`（capability/non-capability 与模块清单以 `25-terai-capability-removal-ddd-redivision-2026-06-25.md` 为准）; split the approved ADR into issues only when coordination requires it.
- Fuzzy requirement: use `grill-with-docs` after onboarding; ask only questions that change scope, behavior, success criteria, or risk.
- Old code understanding or source tutoring: use `tafs-mentor` after onboarding. Keep `tafs-mentor` focused on code explanation and learning notes.
- Bug, incident, failing test, or performance issue: use `diagnose`; reproduce or build a read-only evidence loop before root-cause claims.
- Clear implementation issue: use `tdd`; propose interface, tests, risks, and acceptance before editing unless the user explicitly requested a small direct edit.
- Architecture review or refactor opportunity: use `improve-codebase-architecture`; default to read-only findings first.
- PRD or issue work: use `to-prd`, `to-issues`, or `triage`; use local Markdown unless the user explicitly requests a remote tracker.

## Common Source Routes

- Project direction/current facts: `tafs_sidebar/10-terai-onboarding-workflow.md`, `tafs_sidebar/11-terai-current-facts.md`, latest `tafs_sidebar/meeting_log/*_Terai.txt`.
- Architecture route/reference stack: `tafs_sidebar/13-terai-clean-architecture-route-decision.md`, `tafs_sidebar/16-terai-reference-stack-convergence-2026-06-17.md`, `tafs_sidebar/14-agent-framework-reference-survey-2026-06-16.md`, `tafs_sidebar/15-coding-agent-product-reference-2026-06-16.md`.
- tafs architecture: `tafs_sidebar/INDEX.md`, `tafs_sidebar/17-current-service-chain-and-module-map-2026-06-18.md`, `tafs_sidebar/02-architecture-map.md`, `tafs/internal/httpapi/router.go`, `tafs/internal/worker/`, `tafs/internal/agent/`.
- Chat/agent flow: read `tafs_sidebar/17-current-service-chain-and-module-map-2026-06-18.md` first for `serve` / `Supervisor` / parent-side `Worker` / worker `child` / `agent` boundaries, then `tafs_sidebar/09-chat-flow-mainline.md` and `tafs_sidebar/03-module-notes/worker-agent-tools.md`.
- Plugin/skill/MCP: `tafs_sidebar/03-module-notes/plugin-system.md`, `tafs/internal/plugin/`, `tafs/internal/tools/`.
- Model/LLM profiles: `tafs_sidebar/03-module-notes/backend-core.md`, `tafs_sidebar/03-module-notes/worker-agent-tools.md`, relevant `tafs` source.
- Documents/search/RAG/vector direction: `tafs_sidebar/11-terai-current-facts.md`, latest meetings, `terai_ye_sidebar/03-module-notes/knowledge-and-skills.md` only as demo input.
- AI search / Terai search integration: `tafs_sidebar/19-ai-search-service-integration-guide-2026-06-21.md`, `tafs_sidebar/11-terai-current-facts.md`, `tafs_sidebar/18-terai-target-architecture-task-record-2026-06-18.md`. Current route (2026-06-25, see `25-terai-capability-removal-ddd-redivision-2026-06-25.md`): `ai_search` is the `搜索`(Search) feature subdomain — UI-first via its REST controller (trusted backend/user injection), then exposed to the model via the subdomain `agent 工具面`; every model-initiated call routes through `运行编排`→`运行治理` (no bypass). The terms `Capability Module` / `CapabilityRuntime` / `UI|Agent Capability Surface` are removed.
- Context / memory / session architecture: `tafs_sidebar/21-terai-context-memory-module-2026-06-23.md`, `tafs_sidebar/18-terai-target-architecture-task-record-2026-06-18.md`, `tafs_sidebar/20-terai-observability-module-2026-06-22.md`. Current route is `Context & Memory Module` with `Session Domain` / `Context Domain` / `Memory Domain`; V1 uses `RunEvent/EventLog` as AgentRun fact source, `Conversation Display Projection` for UI history, and lightweight `ContextAnchor` instead of full `ContextSnapshot`. `Prompt Assembly Module` is a sibling module: `Prompt Rendering Pipeline` consumes `ContextPackage` and produces `PromptBundle`; older docs that mention `PromptContext Pipeline` should be read as this rendering pipeline.
- 模块设计与拆分 / capability 移除后的模块图：`tafs_sidebar/25-terai-capability-removal-ddd-redivision-2026-06-25.md`（权威）。`Capability Module` 与 `Non-Capability Module` 已移除：功能归各功能子域（REST controller + `agent 工具面`）、模型工具唯一咽喉 `运行编排`、治理 `运行治理`、工具来源 `能力来源`、定时任务 `任务调度`；判模块怎么切见本 SKILL 的 `Module Design & Decomposition Rules`。
- Frontend/demo comparison: `terai_ye_sidebar/INDEX.md`, `terai_ye_sidebar/02-architecture-map.md`, `terai_ye_sidebar/05-tafs-comparison.md`, then current `terai_ye` source.
- Coding conventions / Go 实现参考（重构落地阶段）: `tafs_sidebar/terai_code_guide/golang_code_guideline.md`（公司 Go 规范）、`go-modern-guidelines`（现代 Go 习语，按 `go.mod` 版本）、本地 `adk-go`（Google 官方 Go agent 框架，`adk-go-skill` 上手）。adk-go 仅作 Go runtime / 接口 / 包结构参考，不整体复制为内核（见 `16-terai-reference-stack-convergence-2026-06-17.md`）。

## Execution Rules

- Default to Chinese prose; keep commands, paths, fields, and identifiers in English.
- Use evidence: cite files, code, tests, command output, latest meeting records, or explicit user statements.
- Inspect `git status` before edits in any touched Git repo.
- Do not touch unrelated dirty files.
- Treat `/home/ZykLyj/yjdev/tafs` as the default fact/integration source. For code/config/script/runtime-behavior changes, create a Session Worktree under `/home/ZykLyj/yjdev/worktrees/tafs/<branch-slug>/` from an explicit base unless the user explicitly approves another write scope.
- Documentation, skill, and sidebar updates are allowed when the user explicitly asks to write/update docs or preserve a conclusion.
- Every code/config/script/behavior change and every current-source architecture analysis needs docs-sync review; if no doc update is needed, explain why.
- Never persist credentials, tokens, cookies, private keys, or API keys.
- 提交与分支遵循公司规范（`tafs_sidebar/terai_code_guide/代码提交规范 revised.md`、`合并请求和分支管理规范.md`）：MR 一事一议、合并 master 用 Squash 压成一个结构化 commit（`type(scope): 摘要` + 正文 + `Fixes/Closes/For`、`Breaking-Change`、`Release-Notes` footer）；分支从 `origin/master` 切出、只用 `git pull --rebase origin master` 同步、禁 merge commit（线性历史）、短期分支合并后删、禁交二进制、版本用 tag。

## Completion Checklist

- State the files changed, or say no files were changed.
- Report validation commands and results, or why validation was blocked.
- Report docs-sync outcome.
- For committed work, stage only current-task files and use `type(scope): summary` plus a useful body.
- Push only when remote, credentials, and proxy handling are approved.
