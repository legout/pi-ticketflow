# Implementation: pt-2rjt

## Summary
Added worktree lifecycle management to `/ralph-loop` dispatch runs. Each ticket now gets its own git worktree, with automatic merge-on-success and cleanup-on-failure semantics compatible with existing Ralph safety patterns.

## Files Changed
- `tf/ralph_loop.py` - Added worktree lifecycle hooks

## Key Changes

### 1. Import Worktree Functions (line ~16)
Added imports from `tf.ralph`:
- `create_worktree_for_ticket()` - Creates a git worktree for each ticket
- `merge_and_close_worktree()` - Merges changes and removes worktree on success
- `cleanup_worktree()` - Removes worktree without merging on failure
- `git_repo_root()` - Gets the git repository root

### 2. Modified `launch_dispatch()` (line ~580)
- Added `cwd: Optional[Path]` parameter
- Passes `cwd` to subprocess.run() to execute in worktree directory

### 3. Session Reconciliation with Worktree Lifecycle (line ~850)
When a session finishes:
- **On success**: Calls `merge_and_close_worktree()` to merge branch and remove worktree
- **On merge failure**: Preserves worktree and marks ticket as failed for manual resolution
- **On failure**: Calls `cleanup_worktree()` to safely remove worktree without merging

### 4. Ticket Launch with Worktree Creation (line ~930)
Before launching each ticket:
1. Creates worktree using `create_worktree_for_ticket(repo_root, worktrees_dir, ticket)`
2. On failure to create worktree: marks ticket failed, continues to next
3. Launches dispatch with `cwd=worktree_path`
4. On launch failure: cleans up worktree, marks ticket failed

### 5. Session State Tracking (line ~985)
Session info now includes `worktree_path` for later cleanup/merge operations.

## Acceptance Criteria Verification

| Criteria | Status | Implementation |
|----------|--------|----------------|
| Worktree created per ticket | ✅ | `create_worktree_for_ticket()` called before each launch |
| Dispatch launched with worktree cwd | ✅ | `cwd=worktree_path` passed to subprocess |
| Success merges & removes worktree | ✅ | `merge_and_close_worktree()` on success path |
| Failure cleans up safely | ✅ | `cleanup_worktree()` on failure path |
| Merge failure preserves worktree | ✅ | Merge failure returns False, worktree kept, ticket marked failed |

## Ralph Safety Compatibility

- **Component safety**: Preserved - filtering happens before worktree creation
- **Lock ownership**: Preserved - same runId + PID verification
- **Session tracking**: Enhanced - now includes worktree_path
- **Dry-run mode**: Preserved - skips worktree creation in dry-run
- **Signal handling**: Preserved - worktrees are cleaned up via session reconciliation

## Testing

### Dry-run mode
```bash
pi /ralph-loop --dry-run
```
Expected: Shows "Would create worktree and dispatch" for each ticket

### Normal mode
```bash
pi /ralph-loop --max-iterations 5
```
Expected:
1. Creates worktrees in `.tf/ralph/worktrees/{ticket}/`
2. Launches dispatch in worktree cwd
3. On success: merges branch, removes worktree
4. On failure: removes worktree without merge

## Key Decisions

1. **Worktrees stored in `.tf/ralph/worktrees/`**: Consistent with existing `parallelWorktreesDir` config
2. **Branches named `ralph/{ticket}`**: Consistent with existing worktree naming convention
3. **Merge uses `--no-ff`**: Preserves branch history for audit trail
4. **Merge failures preserve worktree**: Allows manual conflict resolution
5. **Launch failures cleanup immediately**: Prevents orphaned worktrees

## Verification
```bash
# Check syntax
python3 -m py_compile tf/ralph_loop.py
# Result: Syntax OK
```
