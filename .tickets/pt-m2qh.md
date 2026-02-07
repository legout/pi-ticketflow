---
id: pt-m2qh
status: closed
deps: [pt-c1yj]
links: [pt-c1yj, pt-gmpy]
created: 2026-02-07T14:23:31Z
type: task
priority: 2
assignee: legout
external-ref: seed-when-executing-tf-backlog-in-an-active-s
tags: [tf, backlog, component:api, component:cli, component:config, component:workflow]
---
# Implement /tf-backlog: default topic from active session root_seed

## Task
Implement session-aware topic resolution so /tf-backlog can be invoked without an argument and will use the active session’s root_seed.

## Context
Active session state is stored in .tf/knowledge/.active-planning.json (tf_cli.session_store). /tf-backlog should consume it to avoid requiring users to re-specify the topic-id.

## Acceptance Criteria
- [ ] /tf-backlog with no args uses active session root_seed (when state=active)
- [ ] If no session is active, behavior remains unchanged (auto-locate only when exactly one topic exists)
- [ ] Explicit topic arg still works and bypasses session default
- [ ] CLI/log output indicates which topic was selected and whether session-defaulting occurred

## Constraints
- Keep session finalization semantics intact (archive+deactivate on success)

## References
- Seed: seed-when-executing-tf-backlog-in-an-active-s



## Notes

**2026-02-07T16:24:55Z**

Implemented session-aware topic resolution for /tf-backlog.

Changes:
- Made topic argument optional in prompts/tf-backlog.md
- Added Session-Aware Topic Resolution (Phase A) steps
- Uses active session's root_seed as default when no argument provided
- CLI output indicates when session-defaulting occurs: [tf] Using session default: {root_seed}
- Explicit topic arg still works and bypasses session default
- Auto-locate fallback preserved when no session active

Commit: 05f82ed
Review: 0 Critical, 0 Major (1 fixed), 1 Minor, 2 Warnings, 5 Suggestions
All 561 tests pass.
