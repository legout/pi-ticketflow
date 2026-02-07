---
id: pt-g53y
status: closed
deps: []
links: []
created: 2026-02-06T12:37:21Z
type: task
priority: 2
assignee: legout
external-ref: plan-auto-planning-sessions-linkage
tags: [tf, backlog, plan, planning-session]
---
# Define planning session schema + atomic JSON store

## Task
Define the v1 JSON schema for planning sessions and implement an atomic read/write store for session files under `.tf/knowledge/`.

## Context
We want seed/spike/plan/backlog artifacts to be auto-linked via an active session pointer file and archived snapshots. The store should be shared by all planning procedures to avoid drift.

## Acceptance Criteria
- [ ] Session JSON schema implemented with `schema_version: 1`.
- [ ] Read/write helpers use atomic writes (tmp + rename) for `.active-planning.json` and snapshot files.
- [ ] Store functions are idempotent (safe to call repeatedly).

## Constraints
- Use stdlib only (json, pathlib, datetime).

## References
- Plan: plan-auto-planning-sessions-linkage



## Notes

**2026-02-06T12:51:52Z**

Implemented planning session schema v1 with atomic JSON store.

Session store module (tf_cli/session_store.py) provides:
- Schema v1 with session_id, state, root_seed, spikes, plan, backlog
- Atomic write operations (temp + rename)
- Idempotent add_spike, set_plan, set_backlog operations
- Session lifecycle: create, archive, resume, complete/deactivate
- Environment support: TF_KNOWLEDGE_DIR override

Commit: 42a6400
All 248 existing tests pass.

Next: pt-cqbn can now use this module for /tf-seed session activation.
