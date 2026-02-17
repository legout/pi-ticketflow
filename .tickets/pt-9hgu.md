---
id: pt-9hgu
status: open
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

