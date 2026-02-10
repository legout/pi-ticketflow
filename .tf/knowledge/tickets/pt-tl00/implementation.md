# Implementation: pt-tl00

## Summary
Fixed a bug in Ralph's retry capping integration that prevented proper detection of max-retries-exceeded tickets.

## Bug Fixed
The `is_ticket_blocked_by_retries()` function in `tf/ralph.py` was checking `retry_state.get("status") == "blocked"`, but the aggregate status field in retry-state.json remains "active" even when the last attempt was blocked (to allow for future retries). The fix now correctly checks the last attempt's status instead of the aggregate status.

## Changes Made

### tf/ralph.py
Fixed `is_ticket_blocked_by_retries()` function (lines 1046-1083):
- **Before**: Checked `retry_state.get("status") == "blocked"` (aggregate status)
- **After**: Checks `last_attempt.get("status") == "blocked"` (last attempt status)

This ensures that tickets with `retry_count >= maxRetries` where the last attempt was blocked are correctly identified and skipped.

## Verification

All 60 retry state tests pass:
```
tests/test_retry_state.py::TestRetryStatePersistence::test_load_nonexistent_file PASSED
tests/test_retry_state.py::TestRetryCounter::test_retry_count_increments_on_blocked PASSED
tests/test_retry_state.py::TestMaxRetriesSkip::test_should_skip_at_limit PASSED
tests/test_retry_state.py::TestMaxRetriesSkip::test_should_skip_exceeds_limit PASSED
... 56 more tests PASSED
```

Integration test verified:
1. Ticket with 3 retries correctly blocked at max_retries=3 ✓
2. Ticket with 2 retries correctly allowed at max_retries=3 ✓
3. Retry counter correctly resets after successful close ✓
4. New ticket with no retry state correctly allowed ✓

## Acceptance Criteria Status

- [x] Ralph reads retry state and stops retrying after `workflow.escalation.maxRetries`
- [x] Ralph progress/history records retry attempt count and final blocked outcome
- [x] Documented/guard against `parallelWorkers > 1` without ticket locking (already in code)

## Files Changed
- `tf/ralph.py` - Fixed `is_ticket_blocked_by_retries()` function

## Artifacts
- No new artifacts created - used existing retry state infrastructure
- Existing: `tf/retry_state.py` (60 tests pass)
- Existing: `tf/ralph.py` integration points

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base
