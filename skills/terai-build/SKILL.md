---
name: terai-build
description: Onboard and drive greenfield development of the Terai multi-user AI agent platform backend in the self-contained `terai` Go repo. Use for Terai architecture, modules, packages, build tasks, implementation, diagnosis, review, or when a fresh agent needs current project context. Terai builds the AI layer greenfield and ports only the Host Kernel from `tafs`.
---

# Terai Build

## Purpose

Act as the thin Terai router. Project facts live in `terai/docs/` and `terai/arch/`; reusable engineering disciplines live in focused skills. Keep here only authority order, route selection, Terai overrides, invariants, and execution rules.

## Quick start

1. Default repo: `{YJDEV}/terai` (`{YJDEV}` is the workspace root). Use it as the working directory; every relative path below is repo-root-relative.
2. Before code or project-file changes, read `AGENTS.md`.
3. Read the task-relevant authority in this order:
   - `docs/architecture.md` — target architecture and invariants.
   - `docs/workflow.md` — T0–T3 delivery, build brief, approval, DoD, and HITL.
   - `docs/current-facts.md` — current implementation facts.
   - `arch/modules.yml` and `arch/glossary-lock.txt` — module/dependency and naming authorities.
   - `docs/build_tasks/` — approved plans, progress, evidence, and reviews.
   - `docs/glossary.md` — project vocabulary.

## Fact priority

Current user instruction > current `terai` source/command output/tests > current Accepted ADR and repo docs/arch > `tafs_sidebar/` > older context. `tafs` is a reference mirror for Host Kernel behavior, not the target authority for the greenfield AI layer.

## Route selection

Skills whose descriptions mark them as explicit-command workflows are user entrypoints: recommend them when useful, but never silently invoke them from this skill. A normal “develop Terai” request still follows the same discipline directly through `terai-build`.

| Situation | Route | Terai result |
| --- | --- | --- |
| Read, explain, or locate current behavior | `terai-build` only | Rebuild facts from repo authority; no mutation. |
| Fuzzy requirement or naming/contract decision | Apply the alignment gates; suggest `/grill-with-docs` when the user wants a dedicated session | Decisions land before a build brief; independent questions may be batched. |
| Huge effort whose route is still obscured by fog | Continue alignment/research; mention `/wayfinder` only with its Terai limitation | Do not persist a map until the user approves how parent/child investigations map to Terai's existing authority. Do not disguise implementation as wayfinding. |
| T3 work whose destination is already clear | Apply `to-spec` semantics to the mandatory PRD; suggest `/to-spec` as the explicit packaging command | Split the epic into multiple build tasks. Apply `to-tickets` semantics and suggest `/to-tickets` only when multi-party collaboration requires `issues.md`. |
| Approved build task or frontier ticket | Suggest `/implement` | Implement one approved slice with `tdd`, validation, docs sync, review, and commit. |
| Bug, failing test, incident, or regression | Use `diagnose` (the local compatibility name for upstream `diagnosing-bugs`) | Build a tight red-capable loop, minimise, and diagnose. Only an authorized fix continues through the applicable T1/T2 gates. |
| Important external architecture, protocol, security, or naming evidence | Use `research` with primary sources | Treat findings as evidence, not Terai decisions; main agent re-verifies load-bearing claims. |
| Unknown state/logic or UI shape that needs a concrete answer | Use `prototype` | Keep it isolated and throwaway; capture the verdict, then design production work through normal gates. |
| Implementation completion | Use `code-review` as one input to the Terai Review Gate | Standards and Spec axes do not replace Architecture/Effect and risk-specific review. |

`tdd`, `domain-modeling`, and `codebase-design` are reusable disciplines under these routes. `teach` and general productivity skills stay outside the Terai delivery path.

## Terai overrides for upstream skills

1. **No generic setup in Terai.** Do not run raw `/setup-matt-pocock-skills`; it may create `.scratch/`, `CONTEXT.md`, or `docs/agents/` as competing authorities.
2. **One task authority.** Terai keeps plans and work records in `docs/build_tasks/<task>/`. For T3, `to-spec` semantics produce the required existing `prd.md`; the epic is split into multiple build tasks. Only multi-party collaboration activates `to-tickets` semantics and the existing `issues.md`. Do not create a second tracker tree.
3. **Draft before ready.** A generated spec or ticket is Draft. Only the parent build task passing Pre-Start Review, clearing Blockers and Decision-needed findings, can make a slice ready for implementation.
4. **Plan remains the contract.** Specs and tickets decompose confirmed work; they never replace the approved `plan.md`, ADR, frozen contracts, or architecture authority.
5. **One frontier slice at a time.** `implement` may start only from an Approved task and a fixed base commit. It must preserve unrelated dirty work, use pre-agreed seams, run `make ci` and applicable real-provider/device smoke, sync docs, pass the Terai Review Gate, then commit.
6. **Review has additional axes.** Generic `code-review` supplies Standards and Spec. Terai additionally checks Architecture/Effect; auth, secret, DB, tool execution, frozen contracts, or LLM-facing work also gets the appropriate security/evidence review.
7. **Use Terai language stores.** `domain-modeling` writes resolved terms to `docs/glossary.md`, architecture identifiers to `arch/glossary-lock.txt`, and durable trade-offs to `docs/adr/` only after the naming and approval gates. Do not create a generic `CONTEXT.md`.
8. **Persist and bound research.** Write every Terai research document under the repo-owned `docs/research/` directory, never `/tmp`; reserve `/tmp` for disposable search, extraction, and prototype intermediates only. Research must record source versions and separate Fact/Inference/Recommendation. Prototypes use no real secrets or production side effects and cannot prove production readiness.
9. **Generated tickets skip triage.** `to-tickets` output is already decomposed work; use `triage` for incoming external/raw requests, not as a mandatory hop after ticket generation.
10. **Wayfinder is not yet mapped.** Terai has no approved parent-map/child-investigation representation. Until the user approves a workflow migration or explicit mapping, do not let `wayfinder` create `.scratch` files or repurpose `docs/backlog/` / `docs/build_tasks/`; use bounded alignment and `research` instead.

## Mandatory gate reference

Before any formal recommendation, alignment decision, build-task Draft→Approved transition, code/project-doc/skill change, or completion claim, read [references/gates.md](references/gates.md) completely and apply every relevant gate. For read-only factual answers, load only the task-relevant repo authority unless the answer itself proposes a decision.

## Invariants

- Provider adapters only parse and validate model tool structure. During a Run Attempt, `run` owns the handling and terminal outcome of every legal model tool-call request, and no domain tool surface may bypass it. An actual model-triggered tool execution attempt may begin through `tool.Registry.Execute` only after `governance` explicitly allows it; prepare errors, governance denials, sibling skips, and execution-budget limits may terminate before execution.
- Execution identity is injected by the authenticated backend.
- LLM SDK imports stay in `internal/llm`.
- Do not introduce Shared Kernel, `common`, `util`, or a global coordinator.

## Execution rules

- Default to Chinese prose; keep commands, paths, and identifiers in English. Explain scenario before terminology.
- Use source, command, test, and repo-doc evidence. Mark Fact, Inference, and Recommendation separately for load-bearing decisions.
- Obtain user approval before frozen HTTP/SSE/RPC/DB contracts, DB migrations, remote push, or internal landing changes.
- Keep secrets, tokens, cookies, private keys, and real passwords out of files, logs, audit, prompts, and generated artifacts; inject live model configuration at runtime.
- Stop when a user-owned decision is unanswered. Discoverable facts should be investigated first.
- After validated file changes, create a focused structured commit without unrelated dirty files. Push still requires separate approval.
- Subagents learning Terai use this skill plus `terai/docs` and `terai/arch`; use `terai-onboarding` only when the user explicitly requests `tafs` migration/reference analysis.
