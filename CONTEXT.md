# Personal Agent OS

Personal Agent OS is a local-first operating handbook and automation context for personal agents. It uses Git-backed Markdown as the language for human review, agent coordination, policy, workflow state, and future runtime automation.

## Language

**Personal Agent OS**:
The canonical handbook that defines personal-agent roles, workflows, data boundaries, HITL gates, reports, and improvement loops.
_Avoid_: AgentOS, YourNextAgentOS, generic agent framework

**Personal Agent OS Runtime**:
The future resident execution layer that observes the **Control Plane** and performs allowed automation under Personal Agent OS policy.
_Avoid_: standalone product, replacement OS, separate agent framework

**Control Plane**:
The Git-backed Markdown files, templates, workflow state, and approval records that form the authoritative source for Personal Agent OS policy and coordination.
_Avoid_: knowledge base, documentation-only handbook, database

**Workflow State**:
Human-editable frontmatter or Markdown status that represents where a durable artifact is in an approved workflow.
_Avoid_: runtime log, hidden daemon state

**Runtime Log**:
Machine-written records of execution attempts, errors, retries, and runtime observations.
_Avoid_: workflow state, source of policy truth

**Approval Record**:
A durable local record that captures a human grant, denial, or correction for an action that requires HITL.
_Avoid_: chat message, transient button click

**Plan-Approved Autonomy**:
A task-scoped grant that lets agents execute inside an approved plan without repeated approval for every allowed step.
_Avoid_: global autonomy mode, session-wide permission, permanent approval

**Core Tool**:
A deterministic built-in Runtime capability for high-frequency, policy-sensitive work.
_Avoid_: ad hoc script, long-tail connector

**Fat Agent Extension Point**:
A future controlled extension point for low-frequency long-tail scripts or APIs that are not worth implementing as **Core Tools**.
_Avoid_: default script execution, unrestricted API access

**Control Plane Event**:
A change in an approved local Control Plane location that the **Personal Agent OS Runtime** may observe and route.
_Avoid_: unapproved mailbox event, browser-history event, implicit external signal

**Execution Workspace**:
A task-scoped Git worktree where the Runtime runner may read and write files for an approved task.
_Avoid_: main working tree, global project permission, user home directory

**Command Template**:
An approved shell command shape whose structure is fixed and whose parameters are constrained by the task plan.
_Avoid_: arbitrary shell access, one-off untracked command, command family

**Env Profile**:
A task-scoped declaration of environment variables and value sources that may be injected into Runtime execution.
_Avoid_: inherited shell environment, global token store, implicit credentials

**Network Intent**:
A task-plan statement that records whether a Runtime command is expected to use the network and why.
_Avoid_: domain firewall rule, connector whitelist, hidden external access

**Private Runtime Log**:
A non-Git local log store for full Runtime stdout, stderr, command, timing, and result records.
_Avoid_: Control Plane artifact, report source by default, project scratch file

## Relationships

- **Personal Agent OS** defines policy and language for one **Personal Agent OS Runtime**
- **Personal Agent OS Runtime** observes **Control Plane Events**
- **Control Plane** contains **Workflow State** and **Approval Records**
- **Runtime Log** records execution history but does not override **Workflow State**
- **Plan-Approved Autonomy** is granted by an **Approval Record**
- **Core Tools** are available before **Fat Agent Extension Points**
- **Execution Workspaces** bound the file impact of approved command execution
- **Command Templates** and **Env Profiles** are approved at task scope
- **Private Runtime Logs** record execution history outside the **Control Plane**

## Example dialogue

> **Dev:** "Can the **Personal Agent OS Runtime** approve this issue and keep going automatically?"
> **Domain expert:** "Only if the **Control Plane** contains an **Approval Record** granting **Plan-Approved Autonomy** for this task; otherwise high-risk work must stop."

> **Dev:** "Can this task run the same test command several times?"
> **Domain expert:** "Yes, if the plan approved that **Command Template** inside the task **Execution Workspace**."

## Flagged ambiguities

- "Agent OS", "AgentOS", and "YourNextAgentOS" were used to mean both the handbook and the automation layer; resolved: **Personal Agent OS** is the handbook and **Personal Agent OS Runtime** is its future execution layer.
- "Markdown docs" was used to mean passive documentation; resolved: Git-backed Markdown in this repository is the **Control Plane** when it carries policy, workflow state, or approval records.
- "Approval" was used to mean both transient chat confirmation and durable permission; resolved: only an **Approval Record** is authoritative for Runtime execution.
- "Shell approval" was used to mean both arbitrary command access and repeatable task commands; resolved: repeatable execution approves a constrained **Command Template**, not unrestricted shell access.
