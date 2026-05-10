# Include LLM Drafting In Runtime V1

Runtime v1 will include LLM Drafting for Runtime Task Drafts, but the model will not execute commands, edit files, or bypass Approval Records. `paos draft <parent>` sends bounded Control Plane text to a privately configured OpenAI-compatible provider, accepts only strict structured output, and renders validated output into Runtime Task Markdown for human review.

The provider configuration lives outside the Git-backed Control Plane, for example in `~/.personal-agent-os/config.yaml`, with secrets referenced by `api_key_env` rather than stored in Markdown. The default LLM Payload includes parent Issue or Plan text plus relevant Control Plane, ADR, and template summaries; it does not include Private Runtime Logs or project source files unless a later approved design expands that boundary.
