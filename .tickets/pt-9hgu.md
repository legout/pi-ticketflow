---
id: pt-9hgu
status: closed
deps: []
links: []
created: 2026-02-17T14:36:52Z
type: task
priority: 2
assignee: legout
external-ref: ralph-loop-parity
tags: [tf, ralph, component:workflow, component:cli]
---
# Implement /ralph-loop lock file lifecycle (acquire, stale recovery, release)

Implement real lock handling for .tf/ralph/dispatch-loop.lock in /ralph-loop orchestration. Ensure runId-aware re-entrant turns, stale lock detection via PID liveness, and guaranteed release on terminal states.

## Acceptance Criteria

Lock file includes runId/pid/startedAt; same runId can continue; different live run blocks; stale lock replaced; lock released on completion/failure.


## Notes

**2026-02-17T16:32:28Z**

Lock file lifecycle implementation complete. All critical and major issues resolved. Implementation includes atomic lock acquisition, signal handler ownership verification, PID reuse protection, and guaranteed release on terminal states. Some follow-up items deferred (test coverage, lock heartbeat, flock()).

**2026-02-17T16:34:04Z**

Implemented lock file lifecycle for /ralph-loop with atomic acquisition, ownership verification, PID reuse protection, and signal handler cleanup. Fixed all Critical and Major issues from review. 4 Critical fixes, 4 Major fixes applied. Tests passing.
