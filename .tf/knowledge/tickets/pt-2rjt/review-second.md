# Review: pt-2rjt

## Overall Assessment
The worktree lifecycle integration is generally well-structured with proper success/failure path handling. However, several edge cases around signal handling, orphaned worktrees, and subprocess failure modes present risks that could leave the repository in an inconsistent state or leak resources over time.

## Critical (must fix)
- `tf/ralph_loop.py:854` - Signal handler does not clean up active worktrees on SIGINT/SIGTERM, causing orphaned worktrees that persist after interruption. The `_release_lock_on_signal` function releases the lock but leaves `state["active"]` sessions with their worktrees dangling.
- `tf/ralph_loop.py:854` - Session reconciliation optimistically assumes `success=True` when a session disappears from `pi /list-background` output, but a crashed or killed session would also disappear. This could lead to incorrectly merging failed work.
- `tf/ralph_loop.py:935` - No handling for `repo_root is None` case. If `git_repo_root()` returns `None` (e.g., not in a git repo), the code skips worktree creation silently but still tries to launch dispatch without a worktree cwd, which violates the ticket requirements.

## Major (should fix)
- `tf/ralph_loop.py:942` - Failed worktree creation increments `startedCount` but doesn't verify if the failure was transient (disk full, permission denied) vs. permanent (invalid ticket name). Transient failures could permanently skip valid tickets.
- `tf/ralph_loop.py:974` - Launch failure cleanup calls `cleanup_worktree()` but ignores any exceptions it might raise. If cleanup fails (e.g., permission denied on worktree removal), the error is swallowed and the worktree becomes orphaned without logging.
- `tf/ralph_loop.py:859` - Merge failure preserves worktree but doesn't record the worktree path in the failed ticket entry. A user wanting to manually resolve the merge conflict must manually locate the worktree directory.
- `tf/ralph_loop.py:566` - `launch_dispatch()` generates a synthetic session ID (`uuid.uuid4()[:8]`) instead of extracting the actual session ID from `pi` output. This creates a mismatch between the tracking ID and the actual pi session, making `/attach {session_id}` fail.

## Minor (nice to fix)
- `tf/ralph_loop.py:942` - Error message "failed to create worktree" doesn't include the underlying reason from `create_worktree_for_ticket()`, making debugging harder.
- `tf/ralph_loop.py:859` - The comment says "worktree preserved for manual resolution" but doesn't document the expected manual workflow (e.g., commands to run, branch name convention).
- `tf/ralph_loop.py:20` - Import block doesn't verify that imported functions exist at runtime; if `tf.ralph` module is missing these functions, the error occurs late during first worktree creation.

## Warnings (follow-up ticket)
- `tf/ralph_loop.py:854` - Session reconciliation uses polling via `pi /list-background` which is inherently racy. A session could complete and be removed between polls, causing the optimistic success assumption to trigger on failures.
- `tf/ralph_loop.py:881` - No timeout mechanism for sessions. A hung dispatch session would never be detected as finished, blocking the worktree cleanup indefinitely.
- `tf/ralph_loop.py:935` - Parallel mode with worktrees creates multiple git worktrees simultaneously which may stress git's locking mechanisms; no backoff/retry logic exists for git contention failures.

## Suggestions (follow-up ticket)
- `tf/ralph_loop.py:854` - Add a `worktrees` command to list orphaned worktrees and allow manual cleanup, or add a `--cleanup-orphans` flag to the loop.
- `tf/ralph_loop.py:881` - Consider adding session heartbeat/timeout detection using `pi /status {session_id}` if available, or track session start time and warn on long-running sessions.
- `tf/ralph_loop.py:566` - Parse actual session ID from `pi` output by capturing the line containing "Session started:" or similar, ensuring tracking consistency.

## Positive Notes
- Good separation of success/failure paths with distinct cleanup behaviors (merge vs. no-merge)
- Worktree path stored in session info enables proper lifecycle tracking
- Dry-run mode correctly skips worktree creation entirely
- Component safety filtering is preserved and applied before worktree creation
- Proper use of `start_new_session=True` detaches subprocess from parent signal handling

## Summary Statistics
- Critical: 3
- Major: 4
- Minor: 3
- Warnings: 3
- Suggestions: 3
