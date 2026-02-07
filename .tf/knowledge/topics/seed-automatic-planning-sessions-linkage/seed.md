# Seed: Automatic planning sessions for seed↔spike↔plan↔backlog linkage

## Vision
Make TF planning feel like a cohesive “session” rather than a set of disconnected topic folders.

Today, seeds, spikes, and plans are created as separate `topics/*` entries. Only `/tf-backlog` creates a strong link (tickets → `external-ref`). Everything else is manual (“remember to add spike docs to sources.md”). This leads to lost context, duplicate research, and confusion about what belongs together.

## Core Concept
Treat `/tf-seed` as the start of a planning session that becomes the “current planning root”. While a session is active, planning commands automatically attach their outputs to that root and record a relationship graph in `.tf/knowledge/`.

Key idea: **persist a minimal session state file** in the knowledge dir and update it as spikes/plans/backlogs are created.

## Key Features (MVP)
1. `/tf-seed` activates a session by default (opt-out via `--no-session`).
2. If a session is already active, `/tf-seed` archives it and switches to the new seed.
3. Multiple sessions per seed: archived snapshots are timestamped and resumable.
4. `/tf-spike` auto-attaches to the active seed session (records spike id + adds cross-references).
5. `/tf-plan` auto-attaches to the active seed session (records plan id + adds “Inputs/Related Topics”).
6. `/tf-backlog` records ticket ids into the session and finalizes it (completed + auto-deactivated).
7. Minimal “resume/list” support via `/tf-seed --resume ...` and `/tf-seed --sessions ...` (no new top-level command).

## Non-Goals (MVP)
- Full UI for navigating the topic graph.
- Automatic semantic clustering of topics.
- Cross-repo/global sessions.
- Modifying `tk` itself.

## Open Questions
- Where should relationship metadata live long-term: session snapshots only, or also in `index.json` entries + topic frontmatter?
- Should resume reactivate the same session id or fork a new session id (default: reactivate same, fork later if needed)?
- What’s the best place to document session behavior so users discover it (README vs docs/workflows.md vs prompt help)?
