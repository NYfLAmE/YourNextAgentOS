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
- 大任务拆分门：当一个 build_task 同时跨多个模块、安全边界、LLM-facing 行为、HTTP/RPC/SSE 契约、凭据/权限、packaging，或预计需要多个 agent session 才能完成时，不得直接把整个 plan 升 Approved 后开写。先在 `docs/build_tasks/<task>/` 下补本地 `prd.md` 和 `issues.md`（除非仓库已有明确 issue tracker 并经用户批准发布远端 issue），把用户价值、验收边界、vertical slices、依赖关系、TDD seams 和 ready-for-agent 范围写清楚；PRD/issue briefs 只分解和治理已确认 build_task，不替代 `plan.md` 的架构契约。用户确认拆分后，再进 `Pre-Start Review Gate`。
- 开工前评审门（开工唯一标志）：任何 build_task 在 Draft→Approved 前必须过 `Pre-Start Review Gate`（见下文），把评审 findings 收敛到位（Blocker 全修、Decision-needed 全部由用户拍板、`Open Questions / Blockers` 清空）后才能升 Approved、进入开工；未过门不得写代码。
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
- 每完成一个对齐点并完成文档更新、验证、commit 后，不得只给"下一步建议"并等待用户输入；必须在同一轮直接进入下一批待对齐点，按模板说明场景、目标语义、候选契约和拍板问题。若多个 open questions/blockers 之间没有前后依赖，可以一次性成组对齐；若必须先回答 A 才能判断 B，则仍逐点收敛。只有用户明确要求暂停/只看状态，或下一步涉及必须单独批准的代码实现、skill 修改、高风险契约变更时，才停下等待。
- 每轮 Terai 协作后提炼用户反馈中的偏好/规则；若需要改 `terai-build` 或仓内工作规则，先说明变动、原因、影响范围，得到用户确认后再执行。
- 指派子 agent 了解 Terai 上下文时，只能要求其通过本 `terai-build` skill 和 `terai/docs`/`terai/arch` 上手；不要让子 agent 使用 `terai-onboarding`，除非用户明确要求分析 `tafs` 参考或移植细节。

## Swagger Documentation Gate

新增或修改前端可调用的 HTTP API 时，Swagger / OpenAPI 文档是同一契约的一部分，不能只改 handler 或 DTO：

1. handler 上方必须同步维护 swaggo 注解；request/response DTO 必须有字段注释和必要的 `example` tag。复杂协议在 `@Description` 中给最小必要示例，示例必须来自当前 DTO/测试，不从旧文档复制。
2. `@Router` 的 method/path 必须以实际 router 注册为准；review 时逐项核对 router、handler 注解和 build_task 契约，不能让 Swagger path 先行漂移。
3. 普通 JSON API 默认使用 TOS response wrapper；Swagger 成功响应写成 `ResponseBody{data=<ConcreteData>}` 或 Terai 当时确认的等价 wrapper 类型，无业务 data 时写 wrapper 空 data，错误响应统一写 wrapper 错误对象。
4. SSE / streaming 端点不套 TOS wrapper；Swagger 必须明确 `text/event-stream`、事件名、每个事件的 `data` payload，以及哪些错误发生在 stream 前、哪些通过 `failed` event 表达。
5. async submit 与 job query 必须拆成不同 data schema；submit 只表示 accepted，不表示业务完成，job query 才表达 `status/progress/result/error`。
6. handler 注解只表达 API contract；业务字段约束、默认值、example 放 DTO；真正的业务语义仍以 build_task/ADR/current-facts 为准。
7. build_task 涉及 HTTP API 时，计划和验证项必须包含 Swagger 更新：运行 `swag init` 或 Terai 当时等价生成命令，并检查生成的 `docs/swagger.*` / `docs/docs.go` 是否有未提交 diff。
8. Terai 的 Swagger 校验应 fail fast：生成失败、生成后有意外 diff、`go test ./...` 或 `make ci` 失败，都不能算任务完成。
9. wrapper 例外必须显式列清单，例如 SSE、上游透传、文件下载；默认不要为方便实现新增隐式例外。
10. Terra/OpenClaw 的 Swagger 规范可作为参考，但不能照搬 Terra 的 API 前缀、TOS 白名单、`super-login` 透传或 `swag init` 失败只 warning 的构建策略。

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

## Pre-Start Review Gate

每个 build_task 在 Draft→Approved（开工）之前，必须过一轮结构化的对抗式复核。**过此门是 build_task 开工的唯一标志：未过门不得写代码。** 它不替代业务语义门 / 接口准入门 / Critical Review Gate，而是把它们串成一次针对已成形 plan（大任务另含 prd/issues）的开工前复核。`Critical Review Gate` 是本门内的一个视角，不是本门本身。

### 谁来评审

主 agent 亲自逐条核对；可选指派 ≥1 个独立只读子 agent 做对抗式复核（一个查正确性/一致性，涉及 auth/凭据/工具执行/secret/DB/冻结契约时再加一个查安全），是否指派由当轮 agent 判断。子 agent 只经 `terai-build` + 仓内 docs 上手。无论是否用子 agent，每条“承重”结论都必须由主 agent 回源码/命令输出/真实数据文件核验后才写进结论，不能直接转述。

### 评审清单（每条结论用 Fact / Inference / Recommendation 分层）

1. **源头核对（不信任 plan 自述）**：plan 里每个外部契约、tool/action id、字段名、错误码、配置项/路径、RPC method、引用的数据值，逐条对当前源码、命令输出、真实数据文件（如 `commands.json`、skill 目录）、arch 配置（`modules.yml`、`.go-arch-lint.yml`、`glossary-lock`）核对。真实源头里不存在、或没有明确派生规则的 id/名称/形状 = Blocker。
2. **slice 就绪与依赖正确**：每个 issue 是真正 ready-for-agent 的纵切、可独立验收（有具体测试接缝）；把每条“消费其它 slice 产物（prompt golden、catalog、schema 等）”的验收项与该 issue 的 Blocked-by 交叉核对，引用了后置/并行 slice 产物 = 依赖错误。
3. **LLM-facing 归属与真实可证**：任何 provider/model/tool-call/prompt/SSE 行为都要由某 slice 拥有，且有真实 provider 可验证的验收点；只能用 fake 打勾、真实链路（多轮 transcript、后续轮次带工具、provider 方言回放等）仍未落地的 slice 是“假接缝” = Blocker。LLM 语义须在 Approved 前对齐，不留到 live smoke 才暴露。
4. **secret/身份不泄露全链路**：把每个 secret、凭据、session 材料、Cookie/CSRF 端到端追每一跳（HTTP→解密→RPC→store→validator→executor/CLI→SSE/audit/log/model-feedback），每跳都要有显式负测；通道未定义（如凭据注入 env vs argv）或缺负测 = Blocker；并确认规范化前就发出的模型可见输出（如 tool args 进 SSE/audit）不会夹带用户贴入的 secret。
5. **不变量守住**：唯一咽喉、身份后端注入、LLM SDK 仅 `internal/llm`、不引入 common/util/shared/全局 coordinator；对 plan 文本和隐含代码改动都查。
6. **冻结契约覆盖**：HTTP/SSE/RPC/DB/config/audit/Swagger 改动有批准记录且完整定义；每个模型可见/前端可见的 result 形状与错误码先冻结，不留给实现期随手写的 golden 去定义。
7. **dev/CI 运行依赖行为**：每个外部运行依赖（文件路径、daemon 地址、打包资源根）在 dev/CI 机器缺失时的行为要有定义（启动 fail-closed / 降级 / 调用时报错）并有 dev 默认值，不能只考虑目标设备。
8. **顺序与 arch 登记时机**：安全/治理/审计/脱敏基线排在可执行/有副作用 slice 之前；新增包与依赖边在第一个 import 它的 slice 就同步进 `modules.yml` + `.go-arch-lint.yml` + `glossary-lock`，不拖到最后 docs slice。
9. **内部一致性**：plan 各节、ADR、glossary、非目标之间不自相矛盾（如 Affected Scope 写了某能力但非目标又排除；声称行为与当前代码不符）。
10. **产物完整**：任务目录有模板三件套（plan/progress/review），大任务另有 prd.md + issues.md；issue 引用的文件（如 progress.md/review.md）真实存在或由指定 slice 创建。

### findings 分类与收敛标准（开工唯一标志）

- 每条 finding 归类：**Blocker**（Approved 前必修）/ **Should-fix**（可延后，但需在 plan 显式记录）/ **Decision-needed**（只有用户能拍板的设计/取舍）。
- Approved 需同时满足：所有 Blocker 已在 plan/issues 修掉；所有 Decision-needed 已由用户拍板并写回 plan（可追溯到场景、目标语义、涉及文件、验收方式）；`Open Questions / Blockers` 一节清空；批准版质量门（无未确认的“建议/可能/暂定/后续看”当执行策略）成立。
- 只有满足上述收敛，build_task 才能 Draft→Approved 并开工。评审结论与收敛过程记入该任务 `review.md`（并按需同步 Issue Decomposition Record / Approval Record）。

## Recommendation Justification Gate

每次给出建议、推荐方案、默认选择、优先级排序或要求用户拍板前，必须给出足够理由，不能只给结论：
1. 先说明推荐服务的具体业务场景和成功标准；没有场景和标准，不得要求用户批准。
2. 明确建议依据来自哪里：当前源码/文档事实、命令输出、用户确认、子 agent 调研、外部参考、还是 agent 推断；推断必须标明。
3. 至少说明 2 个关键选择标准，例如风险、交付速度、可验证性、维护成本、用户价值、权限/安全边界、与 Terai 不变量的一致性。
4. 说明被排除的主要替代方案以及排除理由；如果没有替代方案，也要说明为什么这是一个机械落地而不是设计选择。
5. 明确该建议会扩大或收窄哪些范围，哪些风险仍然存在，后续如何用测试、smoke、review 或文档证明它成立。
6. 对高风险、安全、架构、冻结契约、工具执行、凭据、DB、LLM-facing 行为的建议，必须给出 Fact / Inference / Recommendation 分层；不能把推荐包装成事实。

如果理由不足，应先补充调研或解释，而不是推动用户做决断。用户指出“理由不充分 / 不信服 / 为什么这样选”时，本轮必须先补足论证，再继续推进设计。

## Teaching And Learning Gap Hook

- 默认把用户当作刚毕业的后端工程师，而不是专家；解释 Terai 架构、Go 接口、RPC/SSE/LLM/provider 等概念时，先讲业务场景和不做会怎样，再讲术语、接口和取舍。
- 每次用户明确表示"不理解 / 没概念 / 需要深入解释"时，把它视为知识盲区信号；先在当前回答中讲清楚，再判断是否需要沉淀为项目 learning 记录、glossary 或 skill 规则。
- 知识盲区沉淀不能自动改文件；若需要写入 `terai-build`、仓内 docs 或 learning 记录，先说明变动、原因、影响范围，得到用户确认后再执行并提交 commit。

## Alignment Explanation Template

对齐冻结契约、内部接口或新概念时，必须按用户能理解和拍板的顺序输出；不要先抛实现术语、字段表或代码形状。

默认结构：
1. **业务场景**：谁在什么情况下要做什么；不设计这个点会出现什么实际问题。
2. **当前事实**：如果引用 `tafs`，明确标成 "`tafs` 当前事实"，只说明源码现在如何工作；不得把它直接说成 Terai 目标。
3. **术语解释**：首次出现的英文名词或专有词必须就地解释，用中文说明它在这个场景里是什么。每轮尽量少引入新术语；必要时先停下来教学，不继续推进新方案。
4. **关系边界**：如果同时提到多个机制，必须说明它们是同一问题、上下游关系，还是只是出现在同一链路里的两个独立问题；避免把无关事实并列造成误解。
5. **Terai 目标语义**：说明我们希望 Terai 在这个场景下表现成什么样，不做什么，哪些敏感信息不得传递或持久化。
6. **候选契约**：最后再给 HTTP/SSE/RPC/config/audit/Go DTO 等候选形状，并标明是候选、已确认还是待调研。
7. **拍板问题**：默认每次只收敛一个会影响实现或契约的决策；如果多个 open questions/blockers 互不依赖，可以一次性列出多个拍板问题并标清各自场景、候选契约和影响范围。用户拍板后立刻更新文档、校验、commit，然后在同一轮直接展开下一批对齐点，避免要求用户反复输入"确认/下一步"。如果问题之间存在"必须先回答 A 才能分析或选择 B"的关系，则不得批量推进。

如果用户指出"看不懂 / 术语太多 / 关系不清"，立即停止推进设计，先复盘本次表达哪里违反了先场景后术语、默认初学者解释、Fact/Target/Candidate 分离等规则；本轮不得继续引入新方案，除非用户明确要求继续。

## Feedback Hook

自动分析用户问题和反馈，提炼可复用偏好。只在用户确认后修改 skill 或项目规则；修改后运行轻量校验（如 `personal-agent-os/scripts/manage-skills.sh verify`、`git diff --check`、相关 docs/CI 检查）。
