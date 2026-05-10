---
artifact_type: approval_record
title:
status: approved
approved_at:
approved_by:
runtime_task_ref:
approval_scope:
  - runtime_task
  - execution_workspace
  - command_list
  - env_profile
  - network_intent
  - private_runtime_log
source_refs: []
confidence: medium
risk_level: medium
sent_at: null
late_supplement_for: null
feedback_source: null
target_artifact: null
---

# Approval Record: <Title>

## Runtime Task

Link to the approved Runtime Task.

## Approved Boundary

```yaml
execution_workspace:
  repo:
  mode: dedicated_worktree

command_list:
  - id:
    command:
    allowed_args: {}
    repeatable: true

env_profile:
  mode: empty
  allow: []

network_intent:
  enabled:
  reason:

private_runtime_log:
  storage: private_runtime_directory
  retention: long_term
  redaction: none
```

## Conditions

- The Runtime may execute only the approved Command List.
- The Runtime may write only inside the approved Execution Workspace.
- The Runtime must write full logs to the Private Runtime Log and link references back to the Runtime Task.
- If execution fails, LLM repair may create a draft Runtime Task but must not directly change files.

## Evidence

List source references and what they prove.

## Comments

Append approval discussion or corrections here.
