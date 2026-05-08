# Self Improvement Workflow

This workflow turns user feedback into better agent behavior without allowing uncontrolled policy drift.

## Feedback Channels

Supported channels:

- Codex conversation feedback
- email reply feedback
- journal file comments or `Feedback:` sections

V1 can process email reply feedback only when the reply content is manually provided or exported into a whitelisted location. Direct mailbox ingestion belongs to V2 automation.

## Feedback Record

Use [feedback record template](../templates/feedback-record.md).

Every feedback record must include:

- source channel
- target artifact or workflow
- feedback timestamp
- risk classification
- proposed action
- whether it was auto-applied or needs approval

## Risk Classification

Low-risk feedback:

- wording preference
- report section order
- clearer template prompt
- additional checklist item
- formatting preference

Low-risk feedback may be applied automatically. If multiple low-risk feedback items conflict, the newest feedback wins.

High-risk feedback:

- new data source
- changed data privacy boundary
- changed HITL gate
- changed role responsibility
- changed automatic email policy
- changed Git or remote policy
- changed execution autonomy

High-risk feedback must become a pending decision. Do not update canonical workflow until approved.

## Application Loop

1. Capture feedback.
2. Classify risk.
3. Identify target artifact.
4. For low-risk feedback, update the template or checklist and record the change.
5. For high-risk feedback, create a pending decision entry and stop.
6. During the next relevant task, apply the updated template.
7. Review whether the change improved output quality.

## Quality Bar

Self-improvement is not allowed to optimize for pleasing wording over factual accuracy.

The workflow should improve:

- source attribution
- date accuracy
- actionability
- reduced rework
- clearer approval points
- better separation of facts, assumptions, and decisions

## Regression Rule

If a new template change makes output worse, revert or supersede it with a new feedback record. Keep the record of why the change failed.
