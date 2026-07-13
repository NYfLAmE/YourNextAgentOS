---
name: implement
description: Explicit-command workflow that implements one approved single-session plan or one ready frontier ticket using TDD, validation, project review gates, and a focused commit. Use only when the user explicitly invokes implement.
---

# Implement

Implement one approved slice. Repository instructions and project-specific gates override this generic sequence.

1. **Pin scope and baseline.** Read the repo instructions, the approved plan or ready frontier ticket, and its originating spec when one exists. Select exactly one single-session implementation slice, record the fixed base commit for review, and inspect `git status`. Stop if approval, blockers, or user-owned decisions remain; never implement an entire multi-session spec directly.
2. **Confirm seams.** Use the seams already agreed in the spec or plan. If the work needs a new seam or contract, return to alignment instead of inventing it during implementation.
3. **Build with `/tdd`.** Work one vertical slice at a time. Run the focused test and type/static checks throughout; preserve unrelated dirty files.
4. **Validate and synchronize.** Run the full project check once the slice is green, plus any required integration, live, security, generated-doc, or packaging checks. Update the project facts and work records required by repo instructions.
5. **Review from the pinned baseline.** Invoke `/code-review` with the fixed point. Resolve its findings, then pass any additional project-specific architecture, effect, security, approval, or completion gates.
6. **Commit only the slice.** Stage only in-scope files and create the repository's structured commit. Never push unless separately authorized.

Done only when the slice's acceptance criteria, project gates, checks, docs sync, review, and focused commit are all complete.
