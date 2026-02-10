# Implementation: pt-7hzv

## Summary
Added detailed logging for effective timeout per iteration to make timeout backoff observable.

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Files Changed
- `tf/ralph.py` - Modified `calculate_effective_timeout()` to return debug info tuple, added detailed timeout logging in `ralph_run()` and `ralph_start()`

## Key Decisions
- Modified `calculate_effective_timeout()` to return a tuple of `(effective_timeout_ms, debug_info)` where `debug_info` contains:
  - `base_ms`: Base timeout value
  - `increment_ms`: Increment per iteration
  - `attempt_index`: Current iteration index
  - `max_ms`: Max cap (None if not set)
  - `capped`: Boolean indicating if max cap was applied

- Added detailed log format: `Timeout[iteration=N]: base=Xms + increment=Yms -> effective=Zms max=Mms (capped|uncapped)`

- Logs are emitted once per attempt to avoid spam (satisfies acceptance criteria)

## Acceptance Criteria Verification
- [x] Logs include iteration index and effective timeout in ms
- [x] Logs show base/increment and whether max cap applied
- [x] Logging does not spam excessively (one line per attempt)

## Tests Run
- All 17 timeout backoff tests in `tests/test_utils.py` pass
- All 92 tests in `test_utils.py`, `test_ralph_logging.py`, `test_ralph_state.py` pass
- Manual verification of debug info output confirms correct behavior

## Verification
Run `tf ralph run` or `tf ralph start` with timeout backoff enabled to see logs like:
```
Timeout[iteration=0]: base=600000ms + increment=150000ms -> effective=600000ms
Timeout[iteration=1]: base=600000ms + increment=150000ms -> effective=750000ms
```
