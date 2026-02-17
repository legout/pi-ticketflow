---
id: pt-8qk8
status: closed
deps: [pt-699h]
links: [pt-699h, pt-uu03]
created: 2026-02-13T16:05:22Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-ralph-loop-background-interactive
tags: [tf, backlog, component:api, component:cli, component:workflow]
---
# Implement orphaned session recovery and TTL cleanup

## Task
On Ralph startup, detect stale/orphaned sessions, clean them up, and enforce retention TTL for finished session metadata.

## Context
The approved plan requires robust restart recovery and bounded session retention.
Without cleanup, stale sessions can leak resources and confuse scheduling state.

## Acceptance Criteria
- [ ] Startup scans and marks orphaned sessions from prior runs.
- [ ] Orphaned sessions are killed/cleaned before new scheduling starts.
- [ ] Finished session metadata is retained for a limited TTL then pruned.

## Constraints
- Recovery must be safe and idempotent across repeated starts.

## References
- Seed: seed-add-ralph-loop-background-interactive
- Plan: plan-ralph-background-interactive-shell
- Spike: spike-interactive-shell-execution


## Notes

**2026-02-14T01:45:00Z**

## Implementation Complete

Fixed orphaned session recovery and TTL cleanup for Ralph dispatch sessions.

### Key Fixes
1. **Orphan detection**: Now uses `os.kill(pid, 0)` instead of `waitpid` to check process liveness. This correctly handles orphaned sessions from previous Ralph runs (which are NOT children of the current process).

2. **File locking**: Added `fcntl.flock()` based file locking to prevent concurrent writer corruption of `dispatch-sessions.json`.

3. **Atomic writes**: Session state is now written to a temp file and renamed atomically.

4. **Cleanup tracking**: `cleanup_orphaned_session()` now properly tracks worktree cleanup success and returns `False` if cleanup fails.

### Files Changed
- `tf/ralph/session_recovery.py` - Major refactor with fixes

### Commit
`b5e7c702`

**2026-02-14T02:01:52Z**

Close summary: Applied hardening fixes for session recovery with PID-reuse protection, locked state persistence, and hardened cleanup. Quality gate: PASS. Commit: 6d9c25fb
