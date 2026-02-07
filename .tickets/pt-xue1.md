---
id: pt-xue1
status: closed
deps: [pt-psvv]
links: [pt-psvv, pt-zwns]
created: 2026-02-06T13:51:23Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:cli, component:docs, component:workflow]
---
# Implement --apply: update ticket frontmatter priority safely (+ audit note)

## Task
Implement apply mode that updates the `priority:` field in ticket markdown frontmatter and records an audit note.

## Context
`tk` does not currently expose a dedicated “set priority” command, but tickets are local markdown files in `.tickets/`.

## Acceptance Criteria
- [ ] `--apply` updates `priority:` for selected tickets (only when proposed != current).
- [ ] A backup or reversible change strategy exists (e.g., git diff friendly).
- [ ] Adds a note via `tk add-note` describing old→new + reason.

## Constraints
- Do not change closed tickets unless explicitly requested.

## References
- Seed: seed-pi-command-reclassify-priorities


## Notes

**2026-02-06T14:18:42Z**

Implemented --apply mode for priority-reclassify command.

Changes:
- Added 5 new functions for parsing/updating ticket frontmatter
- Atomic file writes using temp+rename pattern
- Adds audit notes with timestamp, old→new priority, and reason
- Git-friendly diffs (preserves file format)

Commit: 7d12240
Tests: 376 passed
