---
artifact_type: runtime_task
title:
status: draft
parent_refs: []
approval_state: draft
approval_refs: []
risk_level: medium
source_refs: []
confidence: medium
runtime_log_refs: []
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Runtime Task: <Title>

## Parent

Link to the parent Issue or Plan. A Runtime Task is an execution request and does not replace the parent artifact.

## Goal

What approved task outcome should this execution support?

## Execution Spec

```yaml
execution_workspace:
  repo:
  mode: dedicated_worktree
  worktree_root: private_runtime_config

command_list:
  - id:
    command:
    allowed_args: {}
    repeatable: true

env_profile:
  mode: empty
  allow: []

network_intent:
  enabled: true
  reason:

private_runtime_log:
  storage: private_runtime_directory
  retention: long_term
  redaction: none
```

## Approval

Link the Approval Record that approves the Runtime Task, Execution Workspace, Command List, Env Profile, Network Intent, and Private Runtime Log policy.

## Result

Summarize execution result and link Private Runtime Log references. Do not paste full private logs into the Control Plane.

## Repair Plan

If execution fails, summarize the failure and link any draft follow-up Runtime Task. LLM repair must produce a draft Runtime Task rather than directly changing files.

## Comments

Append discussion and review notes here.
