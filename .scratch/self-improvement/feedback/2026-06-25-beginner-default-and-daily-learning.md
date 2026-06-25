---
artifact_type: feedback_record
date: 2026-06-25
timezone: Asia/Shanghai
source_refs:
  - current Cursor/Codex conversation on 2026-06-25 - user asked to be treated as a beginner (fresh-grad backend engineer) and to learn something every day from collaboration
  - workflows/self-improvement.md
  - .scratch/self-improvement/feedback/2026-05-29-communication-efficiency.md
  - skills/terai-onboarding/SKILL.md (先场景后术语 / Architecture Writing Rules)
  - skills/teach/SKILL.md
  - /home/ZykLyj/yjdev/tafs_sidebar/learning/
confidence: high
approval_state: applied
risk_level: low
sent_at: null
late_supplement_for: null
feedback_source: Cursor/Codex conversation
target_artifact: README.md Operating Principles + skills/terai-onboarding/SKILL.md
---

# Feedback Record: 2026-06-25

## Feedback

在评审"新需求接入 + 架构演进方法论"时，agent 一次性抛出了约 27 个未解释的术语（DDD / 演进式架构 / Go 防漂移工具链），用户因此无法对决策分支拍板。用户给出长期协作规则（原话要点）：

- 默认把我当成刚毕业的后端工程师，不是专家（treat me as a beginner, not an expert）；后续引入任何新概念、技术名词、行业术语时，都默认我没接触过。
- 我需要每天都能从我们的对话、交流、工作过程里学到东西；模型/智能体能力虽强，但它直接输出、我没内化的内容形不成我的个人竞争力。
- 协作过程要能解决当前问题（项目 + 技术），也要解决我长期成长的问题，让我在 AI 时代不丢掉基本的学习能力与成长机会。
- 这条规则要记录到 personal-agent-os 与 terai-onboarding 中。

## Source Channel

Cursor/Codex conversation feedback.

## Target

- `README.md` 的 `Operating Principles`（全局，所有 agent/工作流都读）。
- `skills/terai-onboarding/SKILL.md`（Terai 工作的 bootstrap 路由 + 护栏）。
- 与既有 `Communication Efficiency`（`workflows/engineering-delivery.md`）、`先场景后术语`（terai-onboarding SKILL）、`teach` skill、各项目 `learning/` 区配合，不替代它们。

## Classification

Low-risk。

理由：只改沟通/教学的措辞与默认姿态，不新增数据源、不降低 HITL 门、不改角色职责、不改邮件/Git/远端策略、不增加执行自主权。按 self-improvement 工作流，低风险可自动应用。

## Research Basis

沿用 2026-05-29 communication-efficiency 记录的认知科学依据（工作记忆容量有限 ~4 chunks；认知负荷理论把"呈现格式"算作外在负荷；progressive disclosure 先给最小当前任务、细节按需展开）。本条在其上补一层"成长"目标：可执行结论 + 可理解原理一起给，让用户能内化、形成个人竞争力，而不是只接收无法吸收的输出。

## Proposed Change

加入"默认初学者 + 每日可学"协作规则：

- 默认用户是刚毕业的后端工程师；引入任何新概念/术语/行业黑话，默认其未接触过：先一句白话场景，再给术语，每个术语首次出现就地中文解释，不一次堆多个生词。
- 每次协作同时服务两类目标：解决当前问题（项目/技术）+ 用户长期成长。
- 工作暴露真实知识/经验盲区时，默认整理成简明、可回看的记录（项目 `learning/` 的 learning-record + reference，或 `teach` skill），让用户复习、内化。
- 不因为"模型能直接给答案"就跳过解释。

## Action Taken

- Auto-applied：在 `README.md` `Operating Principles` 增加两条原则（Beginner-default communication；Growth is a first-class outcome）。
- Auto-applied：在 `skills/terai-onboarding/SKILL.md` 增加 `Teaching & Growth Rules（默认按初学者讲 + 每日可学）` 小节。
- Auto-applied（上一轮）：把本次 27 个概念整理为 `tafs_sidebar/learning/reference/0003-arch-evolvability-glossary.html` + `learning-records/0003-architecture-evolvability-vocabulary-gap.md`，并补 `GLOSSARY.md` / `RESOURCES.md`。
- Needs approval：无。

## Result Check

后续检查点：用户能否在读字段表/接口名之前，先用自己的话复述一个新概念的"场景 + 一句话定义"；以及每次较大协作后，用户能说出"今天学到的一个可内化的点"。若 agent 又出现一次性堆术语，按 Regression Rule 以新 feedback record 修正。
