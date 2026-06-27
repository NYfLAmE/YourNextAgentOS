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
- 写代码：`build brief（开工说明）→ 用户批准 → 落 docs/build_tasks/<task>/plan.md → contract-first/characterization → walking skeleton + 薄纵切 → make ci 全绿 → review → DoD → docs-sync → 结构化 commit`（见 `terai/docs/workflow.md`）。
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

## Business Semantics Gate

每次改代码或调整架构前，先用用户能判断业务目标的语言说明：
1. 谁在什么场景下要做什么。
2. 当前语义是什么（移植 Host Kernel 时必须说明 `tafs` 当前行为；greenfield 模块说明无当前语义）。
3. Terai 目标语义是什么，明确不做什么。
4. 会影响哪些契约（HTTP/SSE/RPC/DB/config/audit）。
5. 用哪些 characterization/contract/golden/live smoke 证明语义成立。

语义未对齐、DB 未 grill、冻结契约未批准时，先停下讨论，不得为了实现而实现。

## Feedback Hook

自动分析用户问题和反馈，提炼可复用偏好。只在用户确认后修改 skill 或项目规则；修改后运行轻量校验（如 `personal-agent-os/scripts/manage-skills.sh verify`、`git diff --check`、相关 docs/CI 检查）。
