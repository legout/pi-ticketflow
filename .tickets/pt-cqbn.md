---
id: pt-cqbn
status: closed
deps: [pt-g53y]
links: []
created: 2026-02-06T12:37:21Z
type: task
priority: 2
assignee: legout
external-ref: plan-auto-planning-sessions-linkage
tags: [tf, backlog, plan, planning-session]
---
# Implement /tf-seed session activation + archive+switch + --no-session

## Task
Enhance `/tf-seed` so it activates a planning session by default and archives the previous active session when switching; add `--no-session` to preserve legacy behavior.

## Context
A planning session is rooted at the created seed topic and stored in `plan-auto-planning-sessions-linkage`'s session model. This provides automatic linkage for subsequent spikes/plans/backlogs.

## Acceptance Criteria
- [ ] `/tf-seed "idea"` creates/updates `.active-planning.json` with a new `session_id` rooted at the new seed.
- [ ] If a session is active, `/tf-seed` archives it to `sessions/{session_id}.json` and then switches.
- [ ] `/tf-seed --no-session ...` creates seed artifacts without touching active session state.

## Constraints
- No new top-level command; enhance existing `/tf-seed` behavior.

## References
- Plan: plan-auto-planning-sessions-linkage



## Notes

**2026-02-06T12:54:06Z**

Implemented /tf-seed session activation with archive+switch semantics.

Changes:
- Updated prompts/tf-seed.md with session behavior and new flags (--no-session, --active, --sessions, --resume)
- Updated skills/tf-planning/SKILL.md Seed Capture procedure with session management

All 248 tests pass. Session store integration verified.
