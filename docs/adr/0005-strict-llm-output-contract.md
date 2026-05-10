# Require Strict LLM Output Contracts

LLM responses consumed by the Personal Agent OS Runtime must use strict structured outputs such as schema-constrained JSON or function calls. If parsing or validation fails, the Runtime should retry or fail the step rather than infer intent through regular expressions or heuristic cleanup.
