# Review: pt-7jzy

## Critical (must fix)

- `tf/ralph.py:2239-2302` - **Dispatch mode doesn't call completion handlers**. Returns immediately after launch (`return 0`) and never calls `wait_for_dispatch_completion`, `update_dispatch_tracking_status`, or `cleanup_dispatch_tracking`. This means completion is not tracked/reported end-to-end. (_sources: reviewer-general_)
- `tf/ralph_completion.py:123-127` - **EOF handling not implemented**. Code explicitly skips EOF/Ctrl+D and goes straight to SIGTERM/SIGKILL, despite the acceptance criterion that "idle sessions receive graceful EOF before forced kill". The docstring claims EOF is sent but implementation skips it. (_sources: reviewer-general, reviewer-spec-audit, reviewer-second-opinion_)
- `tf/ralph_completion.py:57-78` - **Race condition in poll_dispatch_status()**. TOCTOU vulnerability: between `os.kill(pid, 0)` and `os.waitpid()`, the process could exit/be reaped, causing misleading "process exited" results. (_sources: reviewer_second_opinion_)
- `tf/ralph_completion.py:137-176` - **Orphaned child processes risk**. Termination signals target only the leader PID, not the process group. Child processes can survive SIGKILL, violating "no orphan processes" constraint. (_sources: reviewer-general, reviewer_second_opinion_)

## Major (should fix)

- `tf/ralph_completion.py:70-73` - **poll_dispatch_status() logic bug**. Uses only `status == 0` to mean "still running" and ignores the PID returned by `waitpid`. For a child exiting with code 0, `waitpid` can return `(pid, 0)`, which is incorrectly treated as running. (_sources: reviewer-general_)
- `tf/ralph_completion.py:94` - **Unused parameter**: `eof_wait_ms` is defined but never used in the implementation. (_sources: reviewer-general_)
- `tf/ralph/__init__.py:142-149` - **Duplicate exports**: `DispatchResult` appears twice in `__all__` list. (_sources: reviewer-general_, reviewer_second_opinion_)
- `tf/ralph_completion.py:158-176` - **Uninterruptible sleep (D-state) hang risk**. If process enters D-state, SIGKILL won't terminate it and the wait loop can hang indefinitely. (_sources: reviewer_second_opinion_)
- `tf/ralph_completion.py` - **No context manager support**. Callers must manually handle exceptions and cleanup. If `wait_for_dispatch_completion` raises, `cleanup_dispatch_tracking` is never reached. (_sources: reviewer_second_opinion_)

## Minor (nice to fix)

- `tf/ralph_completion.py:26` - **TERMINATED status never produced**. `DispatchCompletionStatus.TERMINATED` is defined but never returned by `wait_for_dispatch_completion()`. (_sources: reviewer-general_)
- `tf/ralph_completion.py:87` - **Inconsistent termination_method values**. Docstring says `"natural", "eof", "kill"` but actual values are `"natural", "sigterm", "sigkill", "not_running", "failed"`. (_sources: reviewer_second_opinion_)
- `tf/ralph_completion.py:236` - **Polling inefficiency**. Fixed 1-second polling intervals waste CPU during long waits. Consider exponential backoff. (_sources: reviewer_second_opinion_)
- `tf/ralph_completion.py:182` - **Missing type safety**. Uses `Any` type hint for `dispatch_result`; should use forward reference or protocol class. (_sources: reviewer_second_opinion_)

## Warnings (follow-up ticket)

- No tests added for completion polling/timeout termination behavior. High regression risk for process-lifecycle code. (_sources: reviewer-general_)
- If caller doesn't call `wait_for_dispatch_completion` after process exits, child becomes zombie because nothing reaped it. (_sources: reviewer_second_opinion_)
- Signal handler interaction undefined - custom SIGCHLD handlers could affect `waitpid` behavior. (_sources: reviewer_second_opinion_)

## Suggestions (follow-up ticket)

- Add metrics/telemetry hooks to track termination reasons and timing
- Consider using `subprocess.Popen.wait()` directly instead of polling via PID
- Add integration tests for edge cases: process with children, D-state, PID reuse

## Summary Statistics
- Critical: 4
- Major: 5
- Minor: 4
- Warnings: 3
- Suggestions: 3

## Positive Notes

- Good use of dataclasses for result types
- Comprehensive logging at appropriate levels
- Clear separation of concerns between polling, termination, and waiting
- The `DispatchCompletionResult` captures useful diagnostic information

## Acceptance Criteria Status

| Criterion | Status |
|-----------|--------|
| Completion detected from dispatch/session state | ❌ Not wired in ralph.py |
| Idle sessions receive graceful EOF before forced kill | ❌ Not implemented |
| Timeout and forced termination reported | ⚠️ Partial - exists but not wired |
| No orphan processes | ❌ Not guaranteed due to PID-only signaling |
