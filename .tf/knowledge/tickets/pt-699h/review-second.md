# Review: pt-699h

## Overall Assessment
The parallel dispatch implementation for Ralph reuses existing component safety logic and worktree lifecycle management, which is architecturally sound. However, several subtle concurrency and resource management issues exist around process lifecycle, file handle hygiene, and worktree state consistency that could cause resource leaks or incomplete failure handling in production use.

## Critical (must fix)

- `tf/ralph.py:1016-1040` (run_ticket_dispatch) - **Orphaned process risk on parent termination**: The dispatch uses `start_new_session=True` which creates a new process group, but there's no SIGTERM/SIGINT handler to propagate shutdown to child processes. If Ralph is killed (Ctrl+C, SIGTERM from systemd, etc.), the dispatched `pi` processes become orphaned and continue running indefinitely, potentially causing resource exhaustion and concurrent write conflicts to shared files (git repo, state files).

- `tf/ralph.py:1023-1030` - **File handle leak in error path**: If `subprocess.Popen()` raises an exception after `stdout_file` is opened, the file handle is never closed. The `try/except` around Popen doesn't clean up `stdout_file`, leading to FD exhaustion under high parallel load.

- `tf/ralph.py:2680-2710` (parallel subprocess branch) - **Missing zombie process reaping**: The legacy parallel subprocess branch uses `proc.wait()` in a loop after launching all processes. If a process exits between the launch loop and the wait loop, it becomes a zombie until its PID is waited on. With high parallel counts and slow I/O, this creates a zombie window that could exhaust the process table.

## Major (should fix)

- `tf/ralph.py:962-1010` - **No timeout for dispatch polling**: The implementation notes mention using `poll_dispatch_status()` for concurrent completion tracking, but I don't see this function in the provided code. If polling has no timeout, a hung `pi` process (infinite loop in agent code) would block Ralph indefinitely, defeating the purpose of the dispatch backend's non-blocking design.

- `tf/ralph.py:1540-1600` (merge_and_close_worktree) - **Merge conflict leaves dirty worktree state**: If `git merge` fails due to conflicts, the function returns `False` and warns, but doesn't reset the working tree or mark the branch as conflicted. A subsequent Ralph iteration might see the same worktree path and attempt to reuse it, causing confusing errors or accidental commits of conflict markers.

- `tf/ralph.py:968` - **Session ID collision risk with UUID4**: While unlikely, UUID4 collisions are theoretically possible (birthday problem). The code uses `uuid.uuid4()` without checking for existing session IDs in the tracking directory. If a collision occurs, one ticket's results would overwrite another's, causing silent data loss.

## Minor (nice to fix)

- `tf/ralph.py:935-940` - **DEVNULL inheritance creates silent failures**: When `pi_output == "inherit"`, the code uses `subprocess.DEVNULL` for stdout/stderr. This means legitimate errors from `pi` (e.g., "prompt not found") are silently discarded. Users will see "launched" but the process may have immediately failed with no log trail.

- `tf/ralph.py:976-986` - **Immediate exit check is racy**: The `proc.poll()` immediately after Popen checks for immediate exit, but on slow systems (high load, NFS home directories), the process might not have even started by the time poll() is called. A short sleep or retry loop would be more robust.

- `tf/ralph.py:1540-1600` - **Branch deletion on merge failure**: The code comments out branch deletion after successful merge but doesn't delete the branch on merge failure. Accumulating `ralph/{ticket}` branches in the repo over time will slow down git operations and clutter `git branch -a` output.

## Warnings (follow-up ticket)

- `tf/ralph.py:2640-2700` - **Worktree directory collision**: The worktree path is `worktrees_dir / ticket`, but if the same ticket is selected in consecutive iterations (possible with certain `tk ready` queries or manual ticket manipulation), the remove/add sequence races with the still-running previous dispatch. A timestamp or iteration-counter suffix would prevent this.

- `tf/ralph.py:1006-1010` - **JSON capture file path collision**: Multiple parallel dispatches writing to the same `{ticket}.jsonl` file will corrupt the JSONL output. Each parallel worker should use unique filenames (include session_id or PID).

- `tf/ralph.py:860-910` (resolve_execution_backend) - **Config validation doesn't reject unknown backends**: Invalid `executionBackend` values fall through to default without raising an error, which may mask configuration typos (e.g., `"disptach"` silently uses dispatch).

## Suggestions (follow-up ticket)

- Add a `--parallel-dispatch-timeout` flag with a sensible default (e.g., 30 minutes per ticket) to prevent indefinite hangs in parallel dispatch mode.

- Consider using `asyncio` or `concurrent.futures` with proper cancellation support instead of manual polling loops for better resource cleanup on interruption.

- Add a `ralph cleanup` subcommand to find and terminate orphaned dispatch sessions and remove stale worktrees, for operational recovery.

- Log the full command line (including env vars that affect behavior) at debug level for easier reproduction of dispatched sessions.

## Positive Notes

- Reusing `select_parallel_tickets()` for component safety ensures consistent behavior between parallel modes - this is good DRY practice.

- The worktree-based isolation is architecturally correct for preventing file system conflicts between parallel workers.

- The tracking file registration (`dispatch_dir / f"{ticket}.json"`) provides a clean hook for deferred cleanup and status monitoring.

- The dry-run mode properly simulates the full flow including worktree paths, making it useful for testing configuration before live runs.

## Summary Statistics

- Critical: 3
- Major: 3
- Minor: 3
- Warnings: 3
- Suggestions: 4
