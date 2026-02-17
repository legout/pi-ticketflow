---
id: pt-bcu8
status: closed
deps: [pt-xwjw]
links: [pt-xwjw, pt-9lri]
created: 2026-02-10T13:11:20Z
type: task
priority: 2
assignee: legout
external-ref: seed-increase-timeout-on-each-iteration-defau
tags: [tf, backlog, component:tests, component:workflow]
---
# Implement timeout backoff calculation helper

## Task
Implement a helper that calculates effective timeout per iteration using base + iteration*increment, with optional max cap.

## Context
Later iterations should get more time; default increment is 150000 ms.

Plan notes: Implement linear timeout backoff: effective = base + iteration_index * increment (cap with max_timeout when configured). Default increment = 150000 ms.

## Acceptance Criteria
- [ ] Helper accepts (base_ms, increment_ms, iteration_index, max_ms?)
- [ ] Cap behavior is implemented and tested in isolation (unit tests can be separate ticket)
- [ ] Units are consistent (ms) and naming is clear

## Constraints
- Default increment: **150000 ms** per iteration
- Avoid runaway execution time (support max cap and respect max iterations)
- Backwards compatible defaults / behavior

## References
- Seed: seed-increase-timeout-on-each-iteration-defau
- Plan: plan-increase-timeout-on-each-iteration-defau


## Notes

**2026-02-10T14:02:26Z**

Implemented timeout backoff calculation helper.

Changes:
- Added calculate_timeout_backoff() to tf/utils.py with linear backoff formula
- Parameter order: (base_ms, increment_ms, iteration_index, max_ms?)
- Input validation for negative values and max_ms < base_ms
- Default increment: 150000ms

Review fixes applied:
- Critical: Fixed parameter order to match specification
- Major: Added input validation for negative values
- Major: Added validation for max_ms >= base_ms

Commit: f542d89
Quality Gate: PASSED (0 Critical, 0 Major remaining)

**2026-02-10T14:02:26Z**

Implemented timeout backoff calculation helper in tf/utils.py.

Changes:
- Added calculate_timeout_backoff() function with linear backoff formula
- Added DEFAULT_TIMEOUT_INCREMENT_MS constant (150000 ms)
- Included input validation for negative values and max_ms < base_ms
- Function signature: (base_ms, increment_ms, iteration_index, max_ms?)

Commit: e20248a

Quality Gate: PASSED (0 Critical, 0 Major remaining)
