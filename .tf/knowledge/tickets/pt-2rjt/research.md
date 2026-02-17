# Research: pt-2rjt

## Status
Research completed

## Ticket Summary
**Add worktree lifecycle to /ralph-loop dispatch runs**

Create per-ticket worktree before launch, run dispatch in worktree cwd, and merge+close on success or cleanup on failure. Keep semantics compatible with existing Ralph safety.

### Acceptance Criteria
- Worktree created per ticket
- dispatch launched with worktree cwd
- success merges & removes worktree
- failure cleans up safely
- merge failure preserves worktree and marks ticket failed

## Context Reviewed

### Existing Worktree Implementation
Found comprehensive worktree functions in `tf/ralph.py`:

1. **`create_worktree_for_ticket(repo_root, worktrees_dir, ticket, logger)`** (lines ~1575-1616)
   - Creates worktree at `{worktrees_dir}/{ticket}`
   - Uses branch `ralph/{ticket}`
   - Removes existing worktree if present
   - Returns worktree path or None on failure

2. **`merge_and_close_worktree(repo_root, worktree_path, ticket, logger)`** (lines ~1619-1698)
   - Merges branch to main/master with `--no-ff`
   - Removes worktree after successful merge
   - Preserves worktree on merge conflict for manual resolution
   - Returns True on success, False on failure

3. **`cleanup_worktree(repo_root, worktree_path, ticket, logger)`** (lines ~1701-1733)
   - Removes worktree without merging
   - Safe cleanup for failure path
   - Returns True on success

### Current ralph_loop.py Implementation
File: `tf/ralph_loop.py`

**Current `launch_dispatch()` function** (lines ~460-497):
- Launches `pi -p "/tf {ticket} --auto"` via subprocess
- Does NOT create worktrees
- Does NOT handle worktree lifecycle
- Returns `(success, session_id, error_message)`

**Current flow in `run_loop()`**:
1. Reconcile lock
2. Query session status for active sessions
3. Launch new tickets via `launch_dispatch()`
4. Update progress
5. Check completion conditions

### Key Configuration
From settings.json:
- `ralph.parallelWorktreesDir`: `.tf/ralph/worktrees`
- `ralph.parallelKeepWorktrees`: `false`

### Ralph Safety Semantics to Preserve
1. **Component safety**: Parallel mode skips tickets with overlapping component tags
2. **Lock ownership**: Run ID + PID verification
3. **Session tracking**: UUID-based session IDs
4. **Graceful termination**: Signal handlers for cleanup

## Implementation Strategy

### Changes to ralph_loop.py

1. **Add worktree lifecycle to `launch_dispatch()`**:
   - Accept `worktree_path` parameter
   - Pass `cwd=worktree_path` to subprocess

2. **Add worktree management in `run_loop()`**:
   - Before launching: Create worktree via `create_worktree_for_ticket()`
   - Store worktree path in session info
   - On session completion:
     - Success: Call `merge_and_close_worktree()`
     - Failure: Call `cleanup_worktree()`

3. **Import worktree functions from ralph.py**:
   ```python
   from tf.ralph import (
       create_worktree_for_ticket,
       merge_and_close_worktree,
       cleanup_worktree,
       git_repo_root,
   )
   ```

### Files to Modify
- `tf/ralph_loop.py` - Add worktree lifecycle

### Testing Considerations
- Dry-run mode should skip worktree creation
- Merge conflicts should preserve worktree
- Signal handler should clean up worktrees on termination

## Sources
- `tf/ralph_loop.py` - Current dispatch loop implementation
- `tf/ralph.py` - Existing worktree functions
- `.tf/config/settings.json` - Ralph configuration
