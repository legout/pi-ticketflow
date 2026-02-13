# Review: pt-0v53

## Overall Assessment
The implementation adds per-ticket worktree lifecycle functions with integration into Ralph's serial mode. While the core logic appears sound, there are several edge cases around git state management, race conditions in cleanup, and branch naming collisions that warrant attention. The worktree integration correctly respects the dispatch backend flag, but the fall-through to subprocess when worktree creation fails is an implicit behavior change that may surprise users.

## Critical (must fix)
- `tf/ralph.py:1403-1445` (`create_worktree_for_ticket`) - **Silent worktree removal race condition**: The function attempts `git worktree remove` before `git worktree add`, but if a stale worktree exists (e.g., from a crashed previous run), the `remove` may succeed while the directory persists, causing the subsequent `add` to fail. The fallback `shutil.rmtree` runs only if `remove.returncode != 0`, but there's a case where remove succeeds but worktree path still exists.
- `tf/ralph.py:1461-1479` (`merge_and_close_worktree`) - **Ambiguous main branch detection**: The function tries to detect main/master by checking current branch, then attempting checkout. However, if the worktree was created from a different branch (e.g., user is on a feature branch), the merge will target the wrong branch. Should explicitly track the original branch at worktree creation time.
- `tf/ralph.py:1424` - **Worktree branch naming collision**: The branch name `ralph/{ticket}` could collide if multiple Ralph instances run concurrently or if a previous run didn't clean up branches. No check for existing branch before creation.

## Major (should fix)
- `tf/ralph.py:1447-1452` - **No validation of worktree creation success**: The code proceeds even if `add_result.returncode != 0` but logs an error. The caller checks for `None` return, but the None is only returned when returncode != 0. However, the worktree directory may be partially created (git metadata without full checkout), leading to confusing failure modes later.
- `tf/ralph.py:1470-1479` - **Merge failure leaves worktree in inconsistent state**: When merge fails due to conflicts, the worktree is preserved (good), but there's no mechanism to communicate to the user how to access and resolve it. The branch remains but the worktree directory may be partially cleaned up on subsequent runs.
- `tf/ralph.py:1481-1495` - **Worktree removal failure ignored**: If `git worktree remove` fails after successful merge, the fallback `shutil.rmtree` is called but errors are silently ignored. This can leave stale git worktree metadata that breaks future `git worktree` commands.
- `tf/ralph.py:1503-1545` - **Cleanup may remove uncommitted work**: The `cleanup_worktree` function performs force removal (`-f` flag), which will discard any uncommitted changes in the worktree without warning. This is expected behavior for failure cleanup, but should be documented.
- `tf/ralph.py:1153-1175` (`ralph_run` integration) - **Missing worktree cleanup on early return paths**: If `ensure_pi()` or `prompt_exists()` fail before `use_worktree` is determined, no cleanup occurs. While these are early failures, a partially created worktree from a previous run won't be cleaned up.
- `tf/ralph.py:1192-1195` - **Timeout/restart doesn't recreate worktree**: When a ticket times out and restarts, the same worktree path is reused but the worktree is not recreated/refreshed from HEAD. This means changes from the failed attempt persist into the retry, potentially causing divergent behavior between first and subsequent attempts.

## Minor (nice to fix)
- `tf/ralph.py:1424` - **Branch naming doesn't include timestamp/random**: Using just `ralph/{ticket}` makes debugging concurrent runs difficult. Consider adding a short timestamp or random suffix to branch names.
- `tf/ralph.py:1467` - **Merge uses `--no-ff` without explanation**: The merge creates a merge commit even for fast-forward scenarios. This is intentional (preserving branch history), but should be documented in comments.
- `tf/ralph.py:1519-1524` - **Branch deletion on cleanup uses `-D` (force)**: The cleanup function force-deletes the branch even if it hasn't been merged. This is correct for cleanup, but inconsistent with merge_and_close_worktree which preserves branches.
- `tf/ralph.py:1440-1444` - **Silent directory removal fallback**: When git worktree remove fails, the fallback attempts `shutil.rmtree` but ignores all exceptions. Could mask permission errors that user should know about.
- `tf/ralph.py:1833-1866` (`ralph_start` integration) - **Similar missing refresh issue**: The serial mode in `ralph_start` also doesn't recreate worktrees on restart attempts.

## Warnings (follow-up ticket)
- `tf/ralph.py:1153` - **No worktree cleanup on KeyboardInterrupt/SIGTERM**: If Ralph receives a termination signal while a ticket is running, the worktree remains. While this is acceptable (preserves state for debugging), there's no documented recovery procedure for users.
- `tf/ralph.py:582-589` - **Dispatch backend TODO still pending**: The implementation creates worktrees for dispatch backend, but the actual dispatch execution is pending pt-9yjn. This means worktrees are created and used with subprocess fallback, which is correct but may create unnecessary overhead when users want pure subprocess mode.
- `tf/ralph.py:1066-1071` - **Parallel mode worktrees not integrated**: The new worktree functions are only used in serial mode. Parallel mode has its own worktree creation logic that duplicates some functionality but doesn't use these new helper functions. This creates maintenance burden and potential divergence.

## Suggestions (follow-up ticket)
- Add a `ralph worktree list` or `ralph status` command to show active worktrees for debugging.
- Consider adding worktree age tracking and automatic cleanup of stale worktrees (older than N hours).
- Document recovery procedure: if merge fails, user should run `git worktree list` and manually resolve.
- Add a `--keep-worktrees` flag specific to dispatch mode (currently only parallel mode respects `parallelKeepWorktrees`).
- Consider adding a pre-flight check that validates git worktree capability and available disk space before starting.

## Positive Notes
- Clean separation of concerns with three distinct lifecycle functions.
- Proper integration with existing `parallelWorktreesDir` config option.
- Correct handling of the success vs failure paths (merge vs cleanup).
- Functions properly exported for testability in `tf/ralph/__init__.py`.
- The dry-run mode correctly skips worktree creation, preventing side effects.
- Good use of type hints and optional logger parameter for flexible usage.

## Summary Statistics
- Critical: 3
- Major: 7
- Minor: 4
- Warnings: 3
- Suggestions: 5
