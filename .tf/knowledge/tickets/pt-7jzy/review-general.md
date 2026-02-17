# Review: pt-7jzy

## Overall Assessment
The implementation adds a new completion module, but the end-to-end dispatch workflow still does not use it, so the ticket’s behavioral acceptance criteria are not met in practice. There are also correctness issues in process status polling and termination semantics that can produce misleading completion state and leave child processes behind.

## Critical (must fix)
- `tf/ralph.py:2239-2302` - Dispatch mode returns immediately after launch (`return 0`) and never calls `wait_for_dispatch_completion`, `update_dispatch_tracking_status`, or `cleanup_dispatch_tracking`. This means completion is not actually tracked/reported by the running workflow, so AC1/AC3 are not satisfied end-to-end.
- `tf/ralph_completion.py:123-127` - The code explicitly skips EOF/Ctrl+D and goes straight to SIGTERM/SIGKILL, despite the requirement that idle sessions receive graceful EOF before forced kill. AC2 is not met.

## Major (should fix)
- `tf/ralph_completion.py:70-73` - `poll_dispatch_status()` uses only `status == 0` to mean “still running” and ignores the PID returned by `waitpid`. For a child exiting with code 0, `waitpid` can return `(pid, 0)`, which is incorrectly treated as running. This drops the success return code and misreports completion details.
- `tf/ralph.py:851-860` + `tf/ralph_completion.py:137-166` - Dispatch processes are started as a new session/process group (`start_new_session=True`) but termination signals target only the leader PID (`os.kill(pid, ...)`), not the process group. Child processes can survive timeout paths, which conflicts with the “no orphan processes” constraint.

## Minor (nice to fix)
- `tf/ralph_completion.py:94` - `eof_wait_ms` parameter is defined but never used.
- `tf/ralph_completion.py:26` - `DispatchCompletionStatus.TERMINATED` is currently never produced by `wait_for_dispatch_completion()`.
- `tf/ralph/__init__.py:142-149` - `DispatchResult` and `run_ticket_dispatch` are duplicated in `__all__`.

## Warnings (follow-up ticket)
- `.tf/knowledge/tickets/pt-7jzy/files_changed.txt:1-2` - Only runtime files changed; no accompanying tests were added for completion polling/timeout termination behavior. This is high regression risk for process-lifecycle code.

## Sections
- **Acceptance Criterion 1: Completion is detected from dispatch/session state** — **Not met end-to-end**. Mechanism exists in `tf/ralph_completion.py`, but no active call path in `tf/ralph.py` uses it.
- **Acceptance Criterion 2: Idle sessions receive graceful EOF (`Ctrl+D`) before forced kill** — **Not met**. EOF is explicitly skipped (`tf/ralph_completion.py:123-127`).
- **Acceptance Criterion 3: Timeout and forced termination outcomes are reported in progress/logs** — **Partially implemented but not wired**. Result fields exist in `DispatchCompletionResult`, but dispatch execution path does not invoke/update/report completion outcomes.
- **Constraint: Ensure no orphan processes remain after timeout paths** — **Not guaranteed** due to PID-only signaling instead of process-group termination.
