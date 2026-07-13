# Terai Project Gates

本文件承载 Terai 变更、对齐、开工与完成的详细 gate。由 [../SKILL.md](../SKILL.md) 按任务分支加载；仓内事实仍以 `terai/AGENTS.md`、`terai/docs/` 与 `terai/arch/` 为准。

## 目录

- Swagger Documentation Gate
- Business Semantics Gate
- Interface And Concept Gate
- Naming And Reference Research Gate
- Critical Review Gate
- Pre-Start Review Gate
- Review Gate
- Recommendation Justification Gate
- Teaching And Learning Gap Hook
- Alignment Explanation Template
- Feedback Hook

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

## Repo-Owned State Gates

Terai 的 Draft→Approved→Done 状态机、Pre-Start Review Gate、Review Gate、评审人要求、findings 分类与完整清单只由当前仓内 `AGENTS.md` 和 `docs/workflow.md` 定义。本 reference 不复制那套规范；每次执行都必须读取仓内当前版本，不能依赖记忆或本文件旧摘要。

将通用 skills 接入这些仓内闸门时只补以下适配规则：

1. `to-spec` / `to-tickets` 只生成 Draft 输入，不能授予开工权；T3 的 PRD 和多方协作时的 issues 形态以仓内当前规则为准。
2. `implement` 只能接收仓内状态机已经批准的单一 slice；通用的 `ready-for-agent`、frontier 或 tracker 状态不能替代 Approved。
3. `code-review` 的 Standards / Spec 报告只是仓内 Review Gate 的输入；目标架构、目标效果、风险专项、真实验证、docs-sync 和 Done 判定仍执行仓内当前清单。
4. 主agent对承重结论负责，必须回当前源码、命令、测试、真实数据与 `docs/arch` 权威复核；独立只读子agent的报告不能直接充当批准或完成结论。
5. 若通用 skill 与仓内当前闸门冲突，立即停止并以仓内规则为准；不得靠本地 override 降低审批、证据或安全要求。

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
4. **领域层级（先建模，后决策）**：当同一个词可能指向不同层级，或议题涉及批次/成员、预算/计数、重试、状态、清零、所有权、并发或生命周期时，先给最小对象层级，再讨论规则。逐个说明对象的一句话定义、父子关系与基数、创建/完成边界；每个数值或状态必须明确统计对象、递增边界和清零边界。用当前用户场景完整翻译一次，例如“一个 A 包含 N 个 B，每个 B 最多产生一个 C”。简单单对象议题以对象定义作为最小模型，随后直接进入目标语义。
5. **概念校验**：把用户原话映射到第3—4步的规范术语，请用户先核对“我理解的对象、层级和计数单位是否准确”；此时专注修正理解，方案选择放到第9步。完成标准是：每个易混词只有一个当前含义；每个数量规则都指向唯一统计对象；示例中的每个动作都能落到一个明确层级；用户确认该映射。达到这些条件后，才能进入数值、清零策略、错误码、字段名或方案A/B。
6. **关系边界**：说明多个机制是同一问题、上下游关系，还是只出现在同一链路里的独立问题；把跨层规则明确落到其拥有者，并显式说明跨层决策的依据。
7. **Terai 目标语义**：说明我们希望 Terai 在这个场景下表现成什么样，不做什么，哪些敏感信息不得传递或持久化。
8. **候选契约**：最后再给 HTTP/SSE/RPC/config/audit/Go DTO 等候选形状，并标明是候选、已确认还是待调研。
9. **拍板问题**：默认每次只收敛一个会影响实现或契约的决策；如果多个 open questions/blockers 互不依赖，可以一次性列出多个拍板问题并标清各自场景、候选契约和影响范围。用户拍板后立刻更新文档、校验、commit，然后在同一轮直接展开下一批对齐点，避免要求用户反复输入"确认/下一步"。如果问题之间存在"必须先回答 A 才能分析或选择 B"的关系，则不得批量推进。

如果用户指出"看不懂 / 术语太多 / 关系不清"，回到第3—5步重新完成概念校验：指出此前混用了哪些对象或层级，把所有依赖该旧理解的未实施决策重新标成待确认或已被取代，并先同步当前执行性文档。概念校验重新通过后，再继续目标语义和候选方案。

## Feedback Hook

自动分析用户问题和反馈，提炼可复用偏好。只在用户确认后修改 skill 或项目规则；修改后运行轻量校验（如 `personal-agent-os/scripts/manage-skills.sh verify`、`git diff --check`、相关 docs/CI 检查）。
