# Review: pt-2rjt

## Overall Assessment
The worktree lifecycle integration is a good direction and the happy path is mostly wired correctly (create → run in worktree → merge/cleanup). However, there is a high-impact safety gap around unvalidated persisted paths, plus a configuration regression and missing coverage for destructive git operations. I recommend addressing these before considering this ticket done.

## Critical (must fix)
- `tf/ralph_loop.py:891-913`, `tf/ralph.py:1749-1753`, `tf/ralph.py:1792-1795` - `worktree_path` is read from persisted state and used directly in merge/cleanup calls without validating it is under the expected worktrees root. On git-worktree-remove failure, helpers fall back to `shutil.rmtree(worktree_path, ignore_errors=True)`, which can delete arbitrary directories if state is corrupted/tampered. This is a destructive data-loss risk.

## Major (should fix)
- `tf/ralph_loop.py:882` - Worktrees are hardcoded to `ralph_dir / "worktrees"` instead of honoring configured `parallelWorktreesDir`. This diverges from existing Ralph behavior and can break users with non-default worktree locations.
- `tf/ralph_loop.py:880-1015` - No tests were added for the new lifecycle branches (worktree creation failure, launch failure cleanup, success merge path, merge-failure preservation). Given these paths perform git mutations and directory deletion, lack of regression coverage is high risk.

## Minor (nice to fix)
- `tf/ralph_loop.py:881`, `tf/ralph_loop.py:895-913` - If `git_repo_root()` fails during reconciliation, the code silently skips merge/cleanup but still transitions tickets, which can orphan worktrees and make operational recovery harder. Emit explicit error handling and avoid marking success when worktree finalization is impossible.

## Warnings (follow-up ticket)
- `tf/ralph_loop.py:566-597`, `tf/ralph_loop.py:635-637` - Session status is inferred optimistically (missing session => success) and session IDs are synthetic. This currently limits confidence in failure attribution and makes future true-async behavior fragile.

## Suggestions (follow-up ticket)
- `tf/ralph_loop.py:880-1015` - Reuse the strict path-validation pattern already present in `tf/ralph/session_recovery.py` (allowed root + `relative_to` check) before any merge/cleanup action to keep safety logic consistent across Ralph components.

## Positive Notes
- Good separation of lifecycle hooks: create before launch, merge on success, cleanup on failure.
- Merge-failure handling preserves worktree for manual resolution, which is a sensible operational fallback.
- `cwd` plumbing into `launch_dispatch()` is straightforward and easy to reason about.

## Summary Statistics
- Critical: 1
- Major: 2
- Minor: 1
- Warnings: 1
- Suggestions: 1
