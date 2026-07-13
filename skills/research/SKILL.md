---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as an authorized Markdown artifact, using OS temporary storage when repo writes are not authorized. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim and recording source versions, dates, or commit SHAs when relevant. Separate Fact, Inference, and Recommendation for decision-support work.
3. Save it only in the location authorized by repository instructions, such as the current task's research area. If no repo write location is authorized, use the OS temporary directory and ask before promoting it into the repo.
4. Keep secrets and sensitive payloads out of the artifact. Return the path and the primary-source list to the main agent; the main agent re-verifies every load-bearing claim before using it as a project decision.
