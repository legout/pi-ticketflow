---
id: pt-9zhm
status: closed
deps: [pt-cqbn]
links: []
created: 2026-02-06T12:37:21Z
type: task
priority: 2
assignee: legout
external-ref: plan-auto-planning-sessions-linkage
tags: [tf, backlog, plan, planning-session]
---
# Add /tf-seed session UX: --active, --sessions, --resume

## Task
Add session UX flags to `/tf-seed`: `--active`, `--sessions [seed-id]`, and `--resume <seed-id|session-id>`.

## Context
Users need to inspect and reactivate archived sessions (multiple sessions per seed). Resume should reactivate the same session id (no fork in v1).

## Acceptance Criteria
- [ ] `--active` prints the current active session or "none".
- [ ] `--sessions` lists archived/completed session snapshots; supports optional seed-id filter.
- [ ] `--resume` reactivates the latest session for a seed-id, or a specific session-id.
- [ ] Resuming archives the currently active session first (archive+switch semantics).

## Constraints
- Keep output concise; no TUI.

## References
- Plan: plan-auto-planning-sessions-linkage



## Notes

**2026-02-06T12:58:24Z**

Implemented session UX flags for /tf-seed:

--active: Prints current active session (or 'none')
--sessions [seed-id]: Lists archived sessions, optionally filtered
--resume <id>: Resumes session by seed-id or session-id

Files changed:
- tf_cli/seed_cli.py (new - 194 lines)
- tf_cli/cli.py (routing for seed subcommand)
- scripts/tf_legacy.sh (seed_cmd function, usage docs)

Commit: a225427
All 248 tests pass.
