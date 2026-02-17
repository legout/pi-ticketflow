---
id: pt-oa8n
status: closed
deps: [pt-m54d]
links: [pt-m54d, pt-ri6k]
created: 2026-02-10T12:06:01Z
type: task
priority: 2
assignee: legout
external-ref: seed-show-ready-and-blocked-ticket-count
tags: [tf, backlog, component:workflow]
---
# Implement queue-state snapshot helper (ready/blocked/running/done)

## Task
Add a small helper module/function that computes queue-state counts from Ralph's in-memory scheduler state.

## Context
Operators need to see whether progress is slow due to many blocked tickets vs few ready tickets; counts should update as dependencies resolve.
This helper is the single source of truth used by both the progress display and normal logging.

## Acceptance Criteria
- [ ] Helper returns counts: ready, blocked, running, done, total (as available)
- [ ] Blocked is deps-only for MVP; running is excluded from ready
- [ ] No external `tk` calls are required to compute counts

## Constraints
- Avoid expensive recomputation (no repeated full ticket re-listing).
- Do not break existing output contracts; prefer additive output or gated formatting.
- Non-TTY output must be readable (no animated control characters).
- Blocked is deps-only for MVP; exclude running ticket from ready.

## References
- Seed: seed-show-ready-and-blocked-ticket-count
- Plan: plan-ready-blocked-counts-ralph


## Notes

**2026-02-10T12:29:59Z**

Implementation complete.

## Summary
Implemented queue-state snapshot helper (QueueStateSnapshot + get_queue_state) following pt-m54d specification.

## Changes
- Created tf/ralph/queue_state.py with QueueStateSnapshot dataclass
- get_queue_state() computes ready/blocked/running/done from in-memory scheduler state
- get_queue_state_from_scheduler() convenience wrapper for callers without pre-built dep_graph
- Added __str__() format: R:{ready} B:{blocked} (done {done}/{total})

## Review Results
- Fixed 1 Critical: Optional[callable] → Optional[Callable]
- Fixed 1 Major: Removed unused blocked_tickets set
- Quality gate passed (0 Critical/Major remaining)

## Commit
b1dfde8 pt-oa8n: Implement queue-state snapshot helper (ready/blocked/running/done)
