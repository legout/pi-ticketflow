---
id: pt-9lri
status: closed
deps: [pt-bcu8]
links: [pt-bcu8, pt-w3ie]
created: 2026-02-10T13:11:20Z
type: task
priority: 2
assignee: legout
external-ref: seed-increase-timeout-on-each-iteration-defau
tags: [tf, backlog, component:tests, component:workflow]
---
# Add unit tests for timeout backoff calculation (including max cap)

## Task
Add unit tests covering the timeout backoff computation (including iteration indexing and cap behavior).

## Context
We want deterministic and regression-safe behavior for the +150000 ms per-iteration increment.

Plan notes: Implement linear timeout backoff: effective = base + iteration_index * increment (cap with max_timeout when configured). Default increment = 150000 ms.

## Acceptance Criteria
- [ ] Tests cover iteration_index=0 and iteration_index=1 semantics (whichever is chosen)
- [ ] Tests cover cap behavior (max_timeout_ms)
- [ ] Tests cover non-default increment override

## Constraints
- Keep tests fast and hermetic

## References
- Seed: seed-increase-timeout-on-each-iteration-defau
- Plan: plan-increase-timeout-on-each-iteration-defau


## Notes

**2026-02-10T14:06:23Z**

--note Implementation complete: Added comprehensive unit tests for calculate_timeout_backoff function covering iteration index semantics (0 and 1), cap behavior (max_timeout_ms), and non-default increment override. All 34 tests pass. See .tf/knowledge/tickets/pt-9lri/ for artifacts.

**2026-02-10T14:08:10Z**

Added 17 comprehensive unit tests for calculate_timeout_backoff() covering:
- Iteration index semantics (0, 1, 2)
- Cap behavior with max_timeout_ms
- Non-default increment override
- Input validation for negative values

All tests pass. The implementation satisfies all acceptance criteria from the ticket.

**2026-02-10T14:08:54Z**

Implemented comprehensive unit tests for calculate_timeout_backoff() function.

Fixed duplicate TestCalculateTimeoutBackoff class issue - merged both classes into a single comprehensive test class with 17 test methods.

Test coverage includes:
- Iteration index semantics (0, 1, 2, large values)
- Cap behavior (max_ms applied, not applied, exactly at max, None)
- Non-default increment overrides
- Edge cases (zero base, zero increment)
- Input validation (negative values, invalid max_ms)

All 17 tests pass. Commit: 7776abb

**2026-02-10T14:09:58Z**

Implemented unit tests for calculate_timeout_backoff() function.

Changes:
- Added TestCalculateTimeoutBackoff class with 17 test methods to tests/test_utils.py
- Covers iteration_index=0/1 semantics, cap behavior (max_timeout_ms), and custom increment override
- All acceptance criteria satisfied

Reviews:
- 3 parallel reviewers: general, spec-audit, second-opinion
- 0 Critical, 0 Major issues identified
- Quality Gate: PASSED

Tests:
- 17 new tests added
- All tests pass (python -m pytest tests/test_utils.py -v)

Commit: 1b0c59a
