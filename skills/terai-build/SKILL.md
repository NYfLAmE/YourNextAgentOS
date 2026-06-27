---
name: terai-build
description: Onboard and drive greenfield development of the Terai multi-user AI agent platform backend (the self-contained `terai` Go repo). Use when working on the terai project — its architecture, modules, packages, build tasks, or when a fresh agent needs the terai project context. Terai is built from scratch (AI layer greenfield; Host Kernel ported from tafs). This skill is a thin router into the repo's own docs/arch; deep methodology lives in tafs_sidebar, global collaboration rules in personal-agent-os.
---

# Terai Build

## Purpose

薄路由：把上手与开发指针指向 **`terai` 仓库自带的 `docs/` + `arch/`**，不在本 skill 复制项目知识。Terai 是 greenfield 从零构建（仅 AI 可变层从零，Host Kernel 移植自 `tafs`），整体后续作为内网 `terai` 新分支落地、切主线。

## Quick Start

1. 默认仓库：`{YJDEV}/terai`（`{YJDEV}` = 本机 yjdev 工作区根，外网 `/home/ZykLyj/yjdev`）。
2. 进仓改代码前先读 `terai/AGENTS.md`。
3. 按顺序读仓内权威：
   - `terai/docs/architecture.md` —— 目标架构与模块图 + 不变量。
   - `terai/docs/workflow.md` —— greenfield 构建工作流（build brief 闸门、ADR、DoD、CI、HITL）。
   - `terai/docs/current-facts.md` —— 项目当前事实（随开发生长）。
   - `terai/arch/modules.yml` —— 模块→包+允许依赖的唯一事实源；`terai/arch/glossary-lock.txt` —— 命名/术语锁。
   - `terai/docs/build_tasks/` —— 每个任务的批准方案/进度/复核（看当前进度从这里）。
   - `terai/docs/glossary.md` —— 词表（先场景后术语）。

## Fact Priority

当前用户指令 > 当前 `terai` 源码/命令输出/测试 > `terai/docs`(current-facts/adr/architecture) > 团队 sidecar `tafs_sidebar/` > 旧上下文。仓内 `docs/adr` + `arch/` 是落地权威；与 sidecar 冲突时以最新 ADR + 当前源码为准。

## Task Routing

- 新需求落点 / 何时新建模块：用 `tafs_sidebar/26` 决策树（两轴：逻辑住哪 + 怎么被够到）。
- 任何代码/架构/构建任务改动：先过业务语义门（目标业务场景、当前语义、Terai 目标语义、非目标、契约影响、测试证明），与用户对齐后再写 build brief；未对齐不得编码。
- 新需求/新功能/新入口/新内部接口/新字段/新事件/新审计字段/新术语：先过接口与概念准入门（见下文），不得把未讨论过的名称、事件、字段或 tafs 既有设计当成 Terai 已确认上下文。
- 新命名进入 build brief、docs 或代码前，必须先给候选项和取舍，让用户定夺；未经确认的名称只能标为候选。
- 架构、契约、安全、DB、RPC/HTTP/SSE 协议、模块边界、命名等重要判断前，能从成熟实践获益时先做参考调研；优先指派独立子 agent，结果必须分清 Fact / Inference / Recommendation。
- 写代码：`build brief（开工说明）→ 用户批准 → 按 docs/build_tasks/_template/ 落 docs/build_tasks/<task>/plan.md → contract-first/characterization → walking skeleton + 薄纵切 → make ci 全绿 → review → DoD → docs-sync → 结构化 commit`（见 `terai/docs/workflow.md`）。
- 移植 Host Kernel：参考 `terai/docs/references/README.md` + `tafs_sidebar/17`/`03-module-notes`/`24` + `{YJDEV}/tafs` 源码（参考镜像）。

## 不变量（不可违反，见 architecture.md/AGENTS.md）

唯一咽喉（模型工具调用经 run→governance→dispatch，子域工具面不可旁路）；身份后端注入；LLM SDK 仅 `internal/llm`；不引入 Shared Kernel/common/util/全局 coordinator。

## 规则边界

- **项目专属**（架构/工作流/命名/结构/防漂移）：本 skill + `terai/docs` + `terai/arch`。
- **全局协作规则**（教学与成长、HITL/信息不足先停、Live LLM 测试、安全不落密钥）：`personal-agent-os`。
- **决策史与方法论**：团队 sidecar `tafs_sidebar/`（`28` 路线/结构/命名、`26` 演进、`25` 模块图、`22` 防漂移）。

## Execution Rules

- 默认中文；命令/路径/标识符用英文。先场景后术语，默认按初学者讲。
- 用证据：源码、命令输出、测试、仓内 docs。
- 改"冻结契约"(HTTP/SSE/表/RPC)、改 DB、push 远端、改内网落地 —— 必须先取得用户批准。
- 绝不持久化密钥/token/cookie/私钥/真实密码；真实模型配置运行时注入。
- **信息不足或提问未获回答时先停下等用户，不替用户做选择。**
- 每次执行代码/文档/skill 等文件改动并完成校验后，都要提交对应 Git commit，保证变更可追溯、可回滚；只 stage 当前任务相关文件，不夹带无关脏改；提交信息使用结构化格式 `type(scope): summary`，正文说明动机、范围、验证。push 远端仍需用户单独批准。
- 每轮 Terai 协作后提炼用户反馈中的偏好/规则；若需要改 `terai-build` 或仓内工作规则，先说明变动、原因、影响范围，得到用户确认后再执行。
- 指派子 agent 了解 Terai 上下文时，只能要求其通过本 `terai-build` skill 和 `terai/docs`/`terai/arch` 上手；不要让子 agent 使用 `terai-onboarding`，除非用户明确要求分析 `tafs` 参考或移植细节。

## Business Semantics Gate

每次改代码或调整架构前，先用用户能判断业务目标的语言说明：
1. 谁在什么场景下要做什么。
2. 当前语义是什么（移植 Host Kernel 时必须说明 `tafs` 当前行为；greenfield 模块说明无当前语义）。
3. Terai 目标语义是什么，明确不做什么。
4. 会影响哪些契约（HTTP/SSE/RPC/DB/config/audit）。
5. 用哪些 characterization/contract/golden/live smoke 证明语义成立。

语义未对齐、DB 未 grill、冻结契约未批准时，先停下讨论，不得为了实现而实现。

## Interface And Concept Gate

凡是提出新的需求、功能点、HTTP 入口、worker RPC、Go struct/interface/function、字段、SSE/event、audit 字段、配置项、DB 表或新术语，必须先对齐：
1. 服务什么用户场景，要实现什么可观察效果；不做会怎样。
2. 目标语义：输入是什么、输出是什么、处理逻辑是什么、错误如何表达、哪些内容不得泄露或持久化。
3. 外部契约：HTTP method/path/body/response/status/SSE 事件、RPC method/params/result/error、config/audit/DB schema 的候选形状。
4. 内部接口：结构体/字段/函数/接口的入参出参、调用方必须知道的约束、依赖和测试面。按 `codebase-design` 的语言，接口不只是 type signature，而是调用方正确使用它必须知道的全部事实。
5. 来源边界：Host Kernel 可借鉴/移植 `tafs`；AI 可变层（run/llm/governance/prompt/tool/search/session 等）必须基于 Terai 当前需求重新设计，不得因 `tafs` 已有实现就默认沿用。
6. 准入状态：明确这是已确认目标、候选方案、参考事实，还是待调研问题；未确认的名称/字段/事件不得写入 build_task 批准版或代码。

对用户解释时先场景后术语。首次出现的新词必须就地解释；如果解释不清业务场景和目标语义，先停下讨论。

Approved 版 `plan.md` 不得把未确认的"建议 / 可能 / 暂定 / 后续看"写成执行策略；每个外部契约、内部接口、字段、事件、配置、测试和代码改动都必须能追溯到用户场景、目标语义、涉及文件和验收方式。涉及 provider/model、stream chunk、错误映射、真实 provider smoke、LLM SDK 或模型配置时，必须先单独对齐 LLM 语义；未对齐前只能写占位边界或阻塞点。

## Naming And Reference Research Gate

新增模块名、包名、接口名、结构体名、字段名、事件名、DB 表名或领域概念名前，必须：
1. 先说明场景和语义，再给 2-4 个候选名称；每个候选说明优点、风险、与 Terai 现有语言的冲突点。
2. 由用户确认最终名称后，才能写入批准版 build brief、docs、glossary、arch 或代码。
3. 对会影响长期架构语言或外部契约的命名，先做参考调研；来源优先官方文档、成熟产品/框架、本地源码或 Terai 权威文档。

参考调研不是给所有小动作加重流程。纯源码事实核对、已确认规则的机械落地、小措辞修正可以跳过；但要在回复中说明跳过原因。调研结论必须区分事实、推断和建议，不能把业界做法直接等同于 Terai 目标。

## Critical Review Gate

任何用户或 agent 提出的需求、结论、接口、模块拆分、命名或实现方案，都要先做批判性复核，再进入 build brief：
1. 它是否真实服务当前用户场景，还是只是为了实现而实现。
2. 它是否过早抽象、浅层转发、重复已有模块职责，或扩大了当前小目标。
3. 它是否把候选方案、参考事实、`tafs` 既有实现误当成 Terai 已确认目标。
4. 是否存在更小、更深、更容易验证的接口或模块形态。
5. 哪些判断来自用户假设，哪些来自 agent 推断，哪些来自源码/文档事实；推断必须标明。

不要默认用户说的或 agent 自己说的就是合理的。先提出反例、风险和替代方案，再与用户对齐；但挑战必须服务于澄清需求和降低返工，不做无意义辩论。

## Feedback Hook

自动分析用户问题和反馈，提炼可复用偏好。只在用户确认后修改 skill 或项目规则；修改后运行轻量校验（如 `personal-agent-os/scripts/manage-skills.sh verify`、`git diff --check`、相关 docs/CI 检查）。
