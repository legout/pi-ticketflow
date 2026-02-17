# Review: pt-699h

## Critical (must fix)
- `tf/ralph.py:1016-1040` (run_ticket_dispatch) - **Orphaned process risk on parent termination**: The dispatch uses `start_new_session=True` which creates a new process group, but there's no SIGTERM/SIGINT handler to propagate shutdown to child processes. If Ralph is killed (Ctrl+C, SIGTERM from systemd, etc.), the dispatched `pi` processes become orphaned and continue running indefinitely, potentially causing resource exhaustion and concurrent write conflicts to shared files (git repo, state files). [sources: review-second]
- `tf/ralph.py:2680-2710` (parallel subprocess branch) - **Missing zombie process reaping**: The legacy parallel subprocess branch uses `proc.wait()` in a loop after launching all processes. If a process exits between the launch loop and the wait loop, it becomes a zombie until its PID is waited on. With high parallel counts and slow I/O, this creates a zombie window that could exhaust the process table. [sources: review-second]
- `tf/ralph.py:1023-1030` - **File handle leak in error path**: If `subprocess.Popen()` raises an exception after `stdout_file` is opened, the file handle is never closed. The `try/except` around Popen doesn't clean up `stdout_file`, leading to FD exhaustion under high parallel load. [sources: review-second]
- `tf/ralph.py:135,2489-2494` - Parallel mode is force-disabled whenever `attemptTimeoutMs > 0` or `maxRestarts > 0`. With the default timeout (`600000ms`) and current project config (`.tf/ralph/config.json:2-3`), `--parallel N` falls back to serial, which blocks the primary goal of parallel scheduling. [sources: review-general]
- `tf/ralph.py:2425-2427,2863-2928` - `execution_backend` is resolved but ignored in the parallel branch. Parallel always launches raw `subprocess.Popen(["pi", "-p", ...])`, so `--dispatch` and `--no-interactive-shell` are not behaviorally distinct in parallel mode. [sources: review-general]

## Major (should fix)
- `tf/ralph.py:1540-1600` (merge_and_close_worktree) - **Merge conflict leaves dirty worktree state**: If `git merge` fails due to conflicts, the function returns `False` and warns, but doesn't reset the working tree or mark the branch as conflicted. A subsequent Ralph iteration might see the same worktree path and attempt to reuse it, causing confusing errors or accidental commits of conflict markers. [sources: review-second]
- `tf/ralph.py:2884-2897,3014` - Worktree creation failures are marked `FAILED` but do not mark the batch as failed; iteration still increments by `len(selected)`. This can under-process tickets while still allowing a successful overall return code. [sources: review-general]
- `tf/ralph.py:2919-2928,2930-3012` - Launching processes is not exception-safe for batch resources. If `open()`/`Popen()` raises mid-batch, previously launched child processes and worktrees are not guaranteed cleanup in this control path. [sources: review-general]
- `tf/ralph.py:962-1010` - **No timeout for dispatch polling**: The implementation notes mention using `poll_dispatch_status()` for concurrent completion tracking, but I don't see this function in the provided code. If polling has no timeout, a hung `pi` process (infinite loop in agent code) would block Ralph indefinitely, defeating the purpose of the dispatch backend's non-blocking design. [sources: review-second]
- `tf/ralph.py:968` - **Session ID collision risk with UUID4**: While unlikely, UUID4 collisions are theoretically possible (birthday problem). The code uses `uuid.uuid4()` without checking for existing session IDs in the tracking directory. If a collision occurs, one ticket's results would overwrite another's, causing silent data loss. [sources: review-second]

## Minor (nice to fix)
- `tf/ralph.py:1540-1600` - **Branch deletion on merge failure**: The code comments out branch deletion after successful merge but doesn't delete the branch on merge failure. Accumulating `ralph/{ticket}` branches in the repo over time will slow down git operations and clutter `git branch -a` output. [sources: review-second]
- `tf/ralph.py:2908-2910,2921-2924` - `jsonl_path` is used as a boolean gate, but the actual output file is written to a different path (`worktree_path/.tf/ralph/logs/...`). This is confusing and increases maintenance cost. [sources: review-general]
- `tf/ralph.py:935-940` - **DEVNULL inheritance creates silent failures**: When `pi_output == "inherit"`, the code uses `subprocess.DEVNULL` for stdout/stderr. This means legitimate errors from `pi` (e.g., "prompt not found") are silently discarded. Users will see "launched" but the process may have immediately failed with no log trail. [sources: review-second]
- `tf/ralph.py:976-986` - **Immediate exit check is racy**: The `proc.poll()` immediately after Popen checks for immediate exit, but on slow systems (high load, NFS home directories), the process might not have even started by the time poll() is called. A short sleep or retry loop would be more robust. [sources: review-second]

## Warnings (follow-up ticket)
- `tests/test_json_capture.py:65-69`, `tests/test_ralph_logging.py:309-370` - Current tests cover argument parsing/log formatting but there is no behavioral integration coverage for parallel-dispatch backend parity, partial launch failure handling, and cleanup invariants. [sources: review-general]
- `tf/ralph.py:860-910` (resolve_execution_backend) - **Config validation doesn't reject unknown backends**: Invalid `executionBackend` values fall through to default without raising an error, which may mask configuration typos (e.g., `"disptach"` silently uses dispatch). [sources: review-second]
- `tf/ralph.py:1006-1010` - **JSON capture file path collision**: Multiple parallel dispatches writing to the same `{ticket}.jsonl` file will corrupt the JSONL output. Each parallel worker should use unique filenames (include session_id or PID). [sources: review-second]
- `tf/ralph.py:2640-2700` - **Worktree directory collision**: The worktree path is `worktrees_dir / ticket`, but if the same ticket is selected in consecutive iterations (possible with certain `tk ready` queries or manual ticket manipulation), the remove/add sequence races with the still-running previous dispatch. A timestamp or iteration-counter suffix would prevent this. [sources: review-second]

## Suggestions (follow-up ticket)
- `tf/ralph.py:2863-2928` + `tf/ralph_completion.py` - Reuse `run_ticket_dispatch` + completion polling utilities in parallel mode so dispatch semantics match serial behavior and backend flags are honored consistently. [sources: review-general]
- Add a `--parallel-dispatch-timeout` flag with a sensible default (e.g., 30 minutes per ticket) to prevent indefinite hangs in parallel dispatch mode. [sources: review-second]
- Add a `ralph cleanup` subcommand to find and terminate orphaned dispatch sessions and remove stale worktrees, for operational recovery. [sources: review-second]
- Consider using `asyncio` or `concurrent.futures` with proper cancellation support instead of manual polling loops for better resource cleanup on interruption. [sources: review-second]
- Log the full command line (including env vars that affect behavior) at debug level for easier reproduction of dispatched sessions. [sources: review-second]
- `tf/ralph.py:2863-3015` - Refactor parallel execution into a single “active batch” structure with `try/finally` cleanup that always closes handles, waits/terminates children, and deterministically cleans or preserves worktrees. [sources: review-general]

## Summary Statistics
- Critical: 5
- Major: 5
- Minor: 4
- Warnings: 4
- Suggestions: 6
