# Implementation: pt-7jzy

## Summary
Implemented dispatch completion handling that treats session exit as authoritative, with graceful EOF/kill fallback for idle sessions and comprehensive reporting of timeout/termination outcomes.

## Files Changed

### New Files
- `tf/ralph_completion.py` - New module for dispatch session completion handling

### Modified Files
- `tf/ralph/__init__.py` - Added exports for new completion handling functions and DispatchResult/run_ticket_dispatch

## Implementation Details

### 1. Dispatch Completion Status Types

Added `DispatchCompletionStatus` enum with states:
- `RUNNING` - Session is still active
- `COMPLETED` - Session finished normally
- `TIMEOUT` - Session terminated due to timeout
- `TERMINATED` - Session was forcefully terminated
- `ERROR` - An error occurred during monitoring

### 2. Dispatch Completion Result

Added `DispatchCompletionResult` dataclass capturing:
- `ticket_id`, `session_id` - Identifiers
- `status` - Final completion status
- `return_code` - Process exit code (if applicable)
- `pid` - Process ID that was monitored
- `duration_ms` - Total time waited
- `termination_method` - How process was terminated ("natural", "sigterm", "sigkill")
- `error` - Error message if something went wrong

### 3. Core Functions

#### `poll_dispatch_status(pid)`
Checks if a dispatch process is still running using `os.waitpid()` with `WNOHANG`.
Returns tuple of `(is_running, return_code)`.

#### `graceful_terminate_dispatch(pid, ...)`
Implements graceful termination sequence:
1. Checks if process is already stopped
2. Sends `SIGTERM` for graceful shutdown
3. Waits up to `kill_wait_ms` for process to exit
4. If still running, sends `SIGKILL`
5. Waits up to 2 seconds for process to be reaped

Returns `(success, method_used)` where method is "sigterm", "sigkill", or "not_running".

#### `wait_for_dispatch_completion(dispatch_result, ...)`
Main monitoring function that:
1. Polls process status at configurable intervals
2. Logs progress every 30 seconds
3. Detects timeout and initiates graceful termination
4. Captures return code when process completes naturally
5. Returns detailed `DispatchCompletionResult`

#### `cleanup_dispatch_tracking(ralph_dir, ticket)`
Removes dispatch tracking file after session completion.

#### `update_dispatch_tracking_status(ralph_dir, ticket, completion_result)`
Updates dispatch tracking JSON file with completion status for audit trail.

## Acceptance Criteria Verification

- [x] **Completion detected from dispatch/session state**: `poll_dispatch_status()` uses `os.waitpid(WNOHANG)` to check process state without blocking
- [x] **Graceful EOF before forced kill**: `graceful_terminate_dispatch()` sends SIGTERM, waits, then SIGKILL if needed
- [x] **Timeout and termination reported**: `wait_for_dispatch_completion()` returns `DispatchCompletionResult` with detailed termination info, including `termination_method` field showing how the process ended
- [x] **No orphan processes**: `graceful_terminate_dispatch()` uses `proc.wait()` equivalent to reap processes after kill

## Integration Notes

The completion handling functions are designed to be used after `run_ticket_dispatch()`:

```python
from tf.ralph import run_ticket_dispatch, wait_for_dispatch_completion

# Launch dispatch
dispatch_result = run_ticket_dispatch(ticket="pt-123", ...)

# Wait for completion with timeout
completion = wait_for_dispatch_completion(
    dispatch_result=dispatch_result,
    ticket_id="pt-123",
    timeout_ms=600000,  # 10 minutes
    logger=logger,
)

# Check result
if completion.status == DispatchCompletionStatus.COMPLETED:
    print(f"Success! Duration: {completion.duration_ms}ms")
elif completion.status == DispatchCompletionStatus.TIMEOUT:
    print(f"Timeout after {completion.duration_ms}ms")
    print(f"Termination method: {completion.termination_method}")
```

## Testing Considerations

- The functions use `os.kill(pid, 0)` for process existence checks
- `os.waitpid(WNOHANG)` is used for non-blocking status checks
- SIGTERM waits are configurable (default 5 seconds)
- SIGKILL waits have a 2-second maximum
- Process reaping is ensured after kill signals
