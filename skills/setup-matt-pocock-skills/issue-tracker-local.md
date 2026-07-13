# Issue tracker: Local Markdown

Tickets and specs (a spec may also be called a PRD) for this repo live as Markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation tickets are one file each at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The map is a file with one child file per decision ticket.

- **Map:** `.scratch/<effort>/map.md` holds Destination, Notes, Decisions-so-far, and Fog.
- **Child ticket:** `.scratch/<effort>/issues/<NN>-<slug>.md`; `Type:` is `research`, `prototype`, `grilling`, or `task`; `Status:` is `claimed` or `resolved`.
- **Blocking:** `Blocked by: NN, NN`. A ticket is unblocked when every listed file is resolved.
- **Frontier:** open, unblocked, unclaimed files under the effort's `issues/`; first by number wins.
- **Claim:** set `Status: claimed` before work.
- **Resolve:** append `## Answer`, set `Status: resolved`, and add a gist plus link to the map's Decisions-so-far.
