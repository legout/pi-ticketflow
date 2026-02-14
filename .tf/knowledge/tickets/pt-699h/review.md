# Review: pt-699h

## Critical (must fix)

- `tf/ralph.py:2485-2490` - **Parallel mode disabled under default timeout settings**: `attemptTimeoutMs` defaults to 600000ms, and any `base_timeout_ms > 0` forces `use_parallel = 1`. This means `tf ralph start --parallel N` silently degrades to serial unless timeout is manually set to 0. [review-general]

- `tf/ralph.py:2859-2924` - **execution_backend not honored in parallel branch**: The parallel path always launches raw `subprocess.Popen(["pi", "-p", ...])` instead of using dispatch orchestration (`run_ticket_dispatch`/completion polling). This makes `--dispatch` vs `--no-interactive-shell` behavior inconsistent in parallel mode. [review-general, review-second]

- `tf/ralph.py:2926-2958` - **No cleanup of remaining processes on batch failure**: On the first non-zero exit code, the function returns immediately without terminating/waiting remaining sibling processes and without cleaning their worktrees/tracking. This can leave background `pi` processes running and leave repository/worktree state partially unmanaged. [review-general]

- `tf/ralph.py:1016-1040` (run_ticket_dispatch) - **Orphaned process risk on parent termination**: The dispatch uses `start_new_session=True` but there's no SIGTERM/SIGINT handler to propagate shutdown to child processes. If Ralph is killed, dispatched `pi` processes become orphaned and continue running indefinitely. [review-second]

- `tf/ralph.py:1023-1030` - **File handle leak in error path**: If `subprocess.Popen()` raises an exception after `stdout_file` is opened, the file handle is never closed, leading to FD exhaustion under high parallel load. [review-second]

## Major (should fix)

- `tf/ralph.py:2880-2893` - **Worktree creation failure increments iteration incorrectly**: When worktree creation fails for one ticket, execution continues but `iteration` is still incremented by `len(selected)`. This can under-process tickets and distort loop accounting. [review-general]

- `tf/ralph.py:2919-2924` - **No try/finally protection for launch loop**: `open(...)` + `subprocess.Popen(...)` in the launch loop are not protected by try/finally. If Popen raises, file handles and newly created worktrees are not cleaned up. [review-general]

- `tf/ralph.py:962-1010` - **No timeout for dispatch polling**: The polling loop has no timeout - a hung `pi` process would block Ralph indefinitely, defeating the dispatch backend's non-blocking design. [review-second]

- `tf/ralph.py:1540-1600` - **Merge conflict leaves dirty worktree state**: If `git merge` fails due to conflicts, the function returns `False` but doesn't reset the working tree or mark the branch as conflicted. Subsequent iterations might reuse the same worktree causing confusing errors. [review-second]

- `tf/ralph.py:968` - **Session ID collision risk with UUID4**: Uses `uuid.uuid4()` without checking for existing session IDs. A collision would cause silent data loss. [review-second]

## Minor (nice to fix)

- `tf/ralph.py:133` - **parallelAutoMerge is dead config**: Defined in defaults but never consumed. Dead config increases confusion. [review-general]

- `tf/ralph.py:2904-2906` - **Misleading jsonl_path usage**: Used only as a boolean gate but actual output path is different (`worktree_logs/...`). Makes reasoning about capture paths harder. [review-general]

- `tf/ralph.py:935-940` - **DEVNULL inheritance creates silent failures**: When `pi_output == "inherit"`, legitimate errors from `pi` are silently discarded with no log trail. [review-second]

- `tf/ralph.py:976-986` - **Immediate exit check is racy**: The `proc.poll()` immediately after Popen may not have started on slow systems. A short sleep or retry loop would be more robust. [review-second]

- `tf/ralph.py:1540-1600` - **Branch deletion on merge failure**: No branch cleanup on merge failure. Accumulating `ralph/{ticket}` branches will slow down git operations. [review-second]

## Warnings (follow-up ticket)

- **No automated coverage evidence** for: parallel mode with `--dispatch`, partial batch launch failure, first-ticket failure with other tickets still running, cleanup behavior for remaining active processes/worktrees. [review-general]

- `tf/ralph.py:2640-2700` - **Worktree directory collision**: If the same ticket is selected in consecutive iterations, the remove/add sequence races with the still-running previous dispatch. [review-second]

- `tf/ralph.py:1006-1010` - **JSON capture file path collision**: Multiple parallel dispatches writing to the same `{ticket}.jsonl` file will corrupt the JSONL output. [review-second]

- `tf/ralph.py:860-910` - **Config validation doesn't reject unknown backends**: Invalid `executionBackend` values fall through to default without raising an error, masking configuration typos. [review-second]

## Suggestions (follow-up ticket)

- Refactor the parallel launcher to use one explicit "active batch" structure with a `finally` cleanup phase that always: 1) waits/terminates remaining children, 2) closes all open handles, 3) cleans or preserves worktrees deterministically. [review-general]

- Reuse the dispatch completion utilities from `tf/ralph_completion.py` in parallel mode so dispatch semantics are consistent across serial and parallel execution. [review-general]

- Add integration tests for backend parity (`dispatch` vs `subprocess`) and failure-path cleanup invariants. [review-general]

- Add a `--parallel-dispatch-timeout` flag with a sensible default (e.g., 30 minutes per ticket) to prevent indefinite hangs. [review-second]

- Consider using `asyncio` or `concurrent.futures` with proper cancellation support instead of manual polling loops. [review-second]

- Add a `ralph cleanup` subcommand to find and terminate orphaned dispatch sessions and remove stale worktrees. [review-second]

## Summary Statistics

- Critical: 5
- Major: 5
- Minor: 5
- Warnings: 4
- Suggestions: 6
