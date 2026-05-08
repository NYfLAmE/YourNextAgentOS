# Risk And HITL Policy

HITL means human-in-the-loop review, approval, or correction.

## Approval Model

Default: risk-based approval.

Agents may proceed without approval for low-risk read, planning, and draft work. Agents must stop for approval before high-risk side effects, scope changes, and policy changes.

## Risk Levels

### Low

Examples:

- read files and docs
- inspect Git status
- summarize whitelisted sources
- create drafts in the approved output directory
- update low-risk wording or checklist items based on latest feedback

Allowed action: proceed and record evidence.

### Medium

Examples:

- create or edit local documentation inside an approved directory
- run tests or checks that may write caches
- update templates without changing policy
- commit approved local changes

Allowed action: proceed only when covered by an approved plan or an explicit user request.

### High

Examples:

- change code, config, scripts, runtime state, or product behavior
- expand data source permissions
- lower approval requirements
- send email or external messages
- push to a remote
- handle credentials or private tokens
- run destructive commands

Allowed action: stop unless the plan explicitly grants permission for that specific class of action.

## Plan-Approved Autonomy

After the user approves a detailed plan, Builder may execute inside that plan:

- edit files listed or implied by the approved scope
- run relevant checks
- update docs required by the change
- commit local changes
- push only if the remote and credential path are already approved

Builder must stop when:

- the work requires changing the plan
- the change touches unexpected files or projects
- tests reveal a different root cause
- credentials are required
- external messages or remote writes are required but not already approved

## Reporting Automation Gates

V1 defines the rules but does not send mail automatically.

Future automated email sending must follow:

- 08:00 daily plan and 22:00 daily snapshot use whitelisted sources only.
- 22:00 email can be sent as a snapshot even if later work continues.
- Late supplements must be linked to the original date.
- The first production email automation requires explicit approval of recipient, sender, schedule, and data sources.

## Self-Improvement Gates

Automatically allowed:

- improve template wording
- add low-risk checklist items
- reorder report sections for readability
- record feedback metadata

Approval required:

- new data source
- new role or changed role responsibility
- changed HITL threshold
- changed email automation policy
- changed Git or remote policy
- any workflow update that increases side effects
