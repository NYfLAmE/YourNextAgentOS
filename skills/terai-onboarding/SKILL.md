---
name: terai-onboarding
description: Bootstrap factual onboarding and task execution for the Terai product and tafs technical base. Use when working on Terai, tafs/Terai architecture, tos-agentd, Terai requirements, Terai beta planning, terai_ye demo comparison, or when user says terai-onboarding, Terai 项目上手, 项目上下文, or wants a fresh agent/GPT to answer or implement Terai-related work.
---

# Terai Onboarding

> **2026-06-26 路线更新**：Terai 已转向 **greenfield 从零重建**（自包含 `terai` 仓库 `{YJDEV}/terai`；仅 AI 可变层从零，Host Kernel 移植自 `tafs`）。**新项目开发请用 `/terai-build` skill + `terai/docs`+`terai/arch`**。本 skill 降级为 **`tafs` 参考来源 / 移植期上手**（理解既有 `tafs` 代码、移植 Host Kernel 时用）；R/S·strangler·P0·10 步抽取·ff 同步等"在 `tafs` 上渐进重构"的工作法在 greenfield 下已退役。权威路线/结构/命名见 `tafs_sidebar/28-terai-greenfield-rebuild-and-workflow-2026-06-26.md`。

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

## Teaching & Growth Rules（默认按初学者讲 + 每日可学）

> 2026-06-25 用户定夺（全局规则，已同步进 `personal-agent-os` README `Operating Principles` 与 `.scratch/self-improvement/feedback/2026-06-25-beginner-default-and-daily-learning.md`）。这是 `先场景后术语` 的扩展，适用于所有解释，不限架构文档。

- 默认用户是刚毕业的后端工程师，不是专家（treat the user as a beginner, not an expert）。引入任何新概念、技术名词或行业术语时，默认用户没接触过：先用一两句白话讲清"这是什么场景下的什么问题、不做会怎样"，再给术语，且每个术语首次出现就地中文解释——绝不一次抛出多个未解释的生词；宁可多一句场景，也不要多一个生词。
- 协作要同时解决两类问题：当前问题（项目 / 技术）+ 用户的长期成长。每次协作都应让用户学到能内化的东西，而不是只交付一段他无法吸收、形不成个人竞争力的输出；可执行结论与可理解原理一起给。
- 当工作暴露真实的知识盲区 / 经验盲区时，默认把它整理成简明、可回看的记录——优先用项目 `learning/` 区（如 `tafs_sidebar/learning/` 的 `learning-records/` + `reference/`，并按需补 `GLOSSARY.md`），或走 `teach` skill——让用户能复习、内化，在 AI 时代保住基本学习与成长能力。
- 不因为模型/智能体"能直接给答案"就跳过解释或跳过沉淀；解释清楚、留下记录，本身就是协作目标的一部分。

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

## Naming & Concept Research Rules（命名与概念引入研究流程）

> 2026-06-26 用户定夺。适用于 Terai/`tafs` 后续引入新的模块名、包名、接口名、结构体名、事件名、DB 表名、领域概念名，尤其是 `agentRun` 这类会影响架构语言和代码边界的命名。

在任何新命名进入 refactor plan、ADR、sidebar 或代码前，必须先走这个流程：

1. **先判实体类型，再讨论名字。** 明确它是产品/领域概念、架构模块/子域、Go package、Go interface/struct、DTO/event、DB table、测试 helper，还是运行时实例。不要把“业务里的一个实体”和“承载它的 package/module”混成一件事。
2. **先说场景和责任。** 用中文说明“这个东西解决哪个业务/工程问题，不引入会怎样”，再给候选英文标识符。
3. **核对 Terai 当前语言。** 先读当前 `tafs` 源码、`11` 当前事实、`25` 模块图、`26` 演进方法论；`Capability Module` / `Non-Capability Module` 已移除，不能继续作为新命名的依据。
4. **做参考调研。** 至少核对一个本地成熟源码参考（如 `{YJDEV}/adk-go`、`{YJDEV}/opencode`、`claude-code-analysis`）或一个官方/一手文档来源。架构级命名优先使用官方文档和本地源码，不用二手博客当权威。
5. **给候选项和取舍。** 对每个候选说明实体类型、适用范围、优点、风险、与 Terai 现有语言的冲突点。
6. **用户确认后才落名。** 未经用户确认，不得把新命名写入代码、ADR 或 refactor task 的批准版计划。确认后的命名必须写入对应 `refactor_tasks/<task>/plan.md`；若是架构级命名，还要同步到合适的 sidebar 事实/ADR/词表。

示例：`agentRun` 首先应被判定为“一次 agent 运行实例 / execution instance”候选，而不是 package 或 module；它是否落成 `AgentRun`、`Invocation`、`Run`、`Execution`，以及 package 是否叫 `agentrun` / `runner` / `runtime` / 其他名字，必须经过上述研究和用户确认。

## Go 命名与结构规范（Naming & Structure Best Practice）

> 2026-06-26 用户定夺（grill 收敛）。这是上面《命名与概念引入研究流程》的"怎么拼标识符"细则，适用于 Terai/`tafs` 所有新增 package / 类型 / 接口命名与放置。依据：Go 官方《Effective Go》+ Go 博客《Package names》(Sameer Ajmani 2015)、公司 Go 规范 §6.2/§6.3、本地 `adk-go`、SKILL《模块设计与拆分规范》。深解见 `tafs_sidebar/learning/learning-records/0004-go-interface-in-consumer-package.md` 与 `learning/GLOSSARY.md`。

1. **包名 = 名词**：短、全小写、单个词、名词，命名"它拥有的领域概念"（正向命名）；禁下划线/驼峰、禁 catch-all（`util`/`common`/`misc`/`non-*`）、禁名词+动词拼接（如 `agentrun`）。
2. **反结巴（stutter）**：类型名不重复包名前缀，前缀由包限定符提供 → `run.Request`（非 `run.RunRequest`）、`run.Store`（非 `run.RunStore`）。一个领域概念的"权威类型"住在与之同名的包里。
3. **跨包可读性靠包限定符**，不靠在类型名里堆领域前缀。
4. **缩写**：沿用既有缩写包名（`llm`/`mcp`，全小写），缩写在类型名里全大写（`LLMProfile`）。
5. **构造器**：`New`/`NewXxx` 工厂；如 `run.New(...) *run.Orchestrator`（对齐 ADK `runner.New`）。
6. **先判实体性质再命名**（沿用上节）：因包名已是 `run`，"一次运行实例"（步骤 2 才引入）不能叫 `run.Run`（结巴），用 `run.Instance`/`run.State`。
7. **返回具体类型、接受接口**：实现方返回具体 struct（不预造 owner 侧接口）；接口按公司 §6.2 定义在**使用方(consumer)包**、只含用到的方法（Go 隐式实现）；唯有被广泛共享的通用契约（`io.Reader`/`llm.Provider`）才提升为 owner/共享包。架构不变量（如"唯一咽喉"）靠 depguard/arch-lint 的**路径规则**强制，不靠把实现做成 owner 侧接口。
8. **统一语言映射**：每个架构模块（中文，如 `运行编排`）↔ 一个 Go 包（`run`）↔ 记入 glossary + `arch/modules.yml`；架构级命名落定后同步进 `arch/glossary-lock.txt`。

已定锚点示例（2026-06-26）：`运行编排` 模块 → package `run`；类型 `run.Request`（原 `RunRequest`）/`run.Event`（步骤1为 `agent.Event` 别名）/`run.Store`（接口，consumer=run 内 Orchestrator）/`run.Orchestrator`（具体 struct，唯一咽喉）/`run.New(...)`。`Capability`/`Non-Capability` 已移除，不得作为新命名依据。

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
- 新需求接入 / 架构演进 / 何时怎么新建模块 / 防漂移机检：`tafs_sidebar/26-terai-arch-evolvability-methodology-2026-06-25.md`（落点决策树两轴 + 新建模块 SOP「适配器优先」+ 预留位置盘点 + 机检规格；与 `22` Tier1、`23` R/S、`25` 模块图与不变量、本 SKILL litmus/必要性检查配套。新需求频繁变动时的"怎么接住"流程入口）。
- Frontend/demo comparison: `terai_ye_sidebar/INDEX.md`, `terai_ye_sidebar/02-architecture-map.md`, `terai_ye_sidebar/05-tafs-comparison.md`, then current `terai_ye` source.
- Coding conventions / Go 实现参考（重构落地阶段）: `tafs_sidebar/terai_code_guide/golang_code_guideline.md`（公司 Go 规范）、`go-modern-guidelines`（现代 Go 习语，按 `go.mod` 版本）、本地 `adk-go`（Google 官方 Go agent 框架，`adk-go-skill` 上手）。adk-go 仅作 Go runtime / 接口 / 包结构参考，不整体复制为内核（见 `16-terai-reference-stack-convergence-2026-06-17.md`）。

## Live LLM Test Rules（真实模型测试规则）

> 2026-06-26 用户定夺。后续 Terai/`tafs` 涉及 LLM、provider、prompt、tool call、agent run、SSE 输出的测试计划，默认不能只靠 mock/fake；必须说明真实 provider 验证如何覆盖。

- 单元测试可以使用 fake/mock，以便稳定验证边界条件、错误路径和快速回归；但只要改动触达 LLM-facing 行为，验收层必须包含真实 LLM provider smoke，除非当前环境不可达或用户明确豁免。
- 每次 refactor plan 的 `Test Plan / 行为锁设计` 必须标注：哪些测试是 deterministic fake/mock，哪些测试是真实 provider，真实 provider 验证哪条业务语义，失败时如何区分代码问题、网络问题、模型服务时段限制和权限/密钥问题。
- 真实模型配置只能通过环境变量、未追踪本地配置或用户当次输入注入；禁止把 API key、token、cookie、私钥、真实用户密码写入 SKILL、`tafs_sidebar`、repo 文件、日志或 refactor task 文档。
- 当前用户指定的真实模型验收目标模型为 `deepseek-v4-pro`。endpoint 与密钥必须在运行时注入；密钥永不落盘。若 endpoint 需要持久记录，必须先确认它不是敏感信息且格式无误，再只记录非密文 endpoint。
- 验证日志和文档可以记录 model id、测试场景、响应状态、错误类型、是否触达 provider、是否出现预期 SSE/tool event；不得记录密钥或含敏感内容的完整 prompt/response payload。

## Information & HITL Rule（需要更多信息就先停下，2026-06-26 用户定夺）

> 全局协作规则。应同步进 `personal-agent-os` README 的 Operating Principles，供所有项目复用。

任何时候只要你判断"要把事情继续做对，需要用户提供更多信息 / 确认 / 凭据 / 决策"，必须**立即停下**，用一两句话说清当前最新情况——已做到哪、卡在哪、为什么需要这条信息、缺它会怎样——然后**等用户提供后再继续**。

- 不要在缺少必要信息时靠猜测硬往前冲，也不要"绕过去先做别的"来回避缺口；那会偏离意图、造成返工、降低开发质量。
- 与 `23` §9 批准闸门互补：§9 管"改动前要批准"，本条管"信息不足时要先问"。
- 例外：能从源码 / 命令输出 / 现有文档自查得到的，先自查（见 `grill-with-docs`："能从代码回答就别问"）；只有自查无法解决、且属于用户才知道的信息（端口/凭据/产品取舍/优先级）时，才停下来问。

## 内外网协作与同步（Cross-net Sync，2026-06-26 用户定夺）

> 详见 `tafs_sidebar/23` §13 + 逐条操作手册 `tafs_sidebar/27-internal-sync-runbook-2026-06-26.md`（内网可读）+ 仓库内 `tafs/docs/internal-sync-runbook.md`。

- 机制：外网重构 `tafs` → 经桥接仓库 `sync`（gitlab.terramaster，内外网共通）git 同步 → 内网 `terai`；代码 git 搬运、不再手工 1:1 重写；**非硬性单向**（内网偶尔改码也可回外网）。
- 内网可访问本 SKILL、`tafs_sidebar`、`personal-agent-os`——规则同一份，不在内网另立。
- 硬约束（安全）：内网机密/密钥绝不进 `sync`/外网可见仓库；密钥运行时注入、永不落盘。
- 提交信息卫生：经 `sync`/内网的提交须**内网中性**（无"外网/内外网"表述）、**无 co-author trailer**；agent 的 commit 包装器会自动注入该 trailer（`--amend` 也会重注入），故外网 sync 导入提交用 `git commit-tree` 生成干净提交。
- 节奏：按里程碑增量同步；push 桥接/远端按 G8 #8 需用户批准。

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
