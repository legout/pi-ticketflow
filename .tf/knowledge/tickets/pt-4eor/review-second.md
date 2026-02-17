# Review: pt-4eor

## Overall Assessment
The implementation successfully integrates the dispatch backend into the serial Ralph loop. The core logic at lines 2780-2920 correctly wires `run_ticket_dispatch()` with `wait_for_dispatch_completion()` and preserves the existing state update contracts via `update_state()`. However, there are resource cleanup edge cases that should be addressed to prevent worktree leaks.

## Critical (must fix)
- No issues found.

## Major (should fix)
- `tf/ralph.py:2788-2794` - Worktree leak on dispatch launch failure. When `dispatch_result.status == "failed"`, the worktree created at lines 2752-2773 is not cleaned up. The code should call `cleanup_worktree()` before setting `ticket_rc = 1` to prevent orphaned worktrees.

## Minor (nice to fix)
- `tf/ralph.py:2797` - Local import inside conditional block. The import `from tf.ralph_completion import update_dispatch_tracking_status` is performed inside the dispatch completion handling block. While functional, moving this to the top-level imports (line 33-39) would improve consistency with the other imports from the same module.
- `tf/ralph.py:2839-2850` - Missing worktree cleanup on timeout restart. When `ticket_rc == -1` (timeout) and `attempt < max_attempts`, the code continues to the next restart iteration without cleaning up the current worktree. This could accumulate orphaned worktrees during timeout/restart cycles. Consider cleaning up the worktree before continuing.

## Warnings (follow-up ticket)
- None.

## Suggestions (follow-up ticket)
- Consider adding a defensive cleanup mechanism that scans for and removes stale worktrees older than a certain threshold on Ralph startup. This would complement the existing session recovery (pt-8qk8) by catching worktrees that may have been orphaned due to crashes or edge cases like those identified above.

## Summary Statistics
- Critical: 0
- Major: 1
- Minor: 2
- Warnings: 0
- Suggestions: 1
