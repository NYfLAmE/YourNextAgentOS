# Split Workflow State And Runtime Log

Human-facing workflow state belongs in Markdown frontmatter or body fields on durable artifacts, while machine execution attempts, retries, errors, and observations belong in a separate Runtime Log. This preserves the Control Plane as editable and reviewable without polluting PRDs, issues, or reports with every runtime attempt.
