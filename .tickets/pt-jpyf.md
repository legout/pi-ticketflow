---
id: pt-jpyf
status: closed
deps: [pt-7l5c]
links: []
created: 2026-02-06T12:37:21Z
type: task
priority: 2
assignee: legout
external-ref: plan-auto-planning-sessions-linkage
tags: [tf, backlog, plan, planning-session]
---
# Implement session finalization in /tf-backlog (record + complete + deactivate)

## Task
Update `/tf-backlog` so when a session is active it records created ticket IDs, writes a completed snapshot, and deactivates the active session pointer.

## Context
This prevents accidental linking after backlog generation and preserves a durable session history.

## Acceptance Criteria
- [ ] After successful ticket creation, session records `backlog.topic`, `backlog.backlog_md`, and `backlog.tickets`.
- [ ] Session snapshot is written to `sessions/{session_id}.json` with `state: completed` + `completed_at`.
- [ ] `.active-planning.json` is removed after completion.
- [ ] Emits a one-line notice when finalizing.

## Constraints
- If ticket creation fails part-way, do not delete the active pointer; write an error note.

## References
- Plan: plan-auto-planning-sessions-linkage



## Notes

**2026-02-06T13:10:46Z**

--note ## Implementation Complete

Implemented session finalization in /tf-backlog prompt:

**Changes:**
- Added session detection at start of backlog generation
- Added Step 11 for session finalization with:
  - Recording of backlog.topic, backlog.backlog_md, and backlog.tickets
  - Session snapshot written to sessions/{session_id}.json with state: archived
  - .active-planning.json removal on success
  - One-line notice: [tf] Session archived: {session_id} ({count} tickets created)
  - Error handling with state: error, leaving active pointer intact for retry

**Review Issues Addressed:**
- Fixed state naming (archived vs completed) for consistency
- Added mkdir -p for sessions directory
- Added explicit error schema with error.message, failed_at, tickets_created
- Added zero-tickets edge case handling
- Added session state validation at start and finalization

**Commit:** 48395eb
