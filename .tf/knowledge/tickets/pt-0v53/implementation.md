# Implementation: pt-0v53

## Summary
Implemented per-ticket worktree lifecycle for dispatch runs in Ralph. This enables each ticket to run in an isolated git worktree when using the dispatch backend, with automatic merge on success and safe cleanup on failure.

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Files Changed
- `tf/ralph.py` - Added worktree lifecycle functions and integrated them into ticket execution flow

### Key Changes

1. **Worktree Functions** (lines ~1244-1410):
   - `create_worktree_for_ticket()` - Creates a git worktree for a ticket
   - `merge_and_close_worktree()` - Merges changes to main branch and removes worktree
   - `cleanup_worktree()` - Safely removes worktree without merging (failure path)

2. **Integration into `ralph_run()`** (lines ~1966-2040):
   - Creates worktree when using dispatch backend (not dry-run)
   - Passes worktree as `cwd` to `run_ticket()`
   - **Fixed**: Now checks return value of `merge_and_close_worktree()` - if merge fails, marks ticket as FAILED instead of COMPLETE
   - **Fixed**: Added deterministic target branch checkout before merge (ensures we're on main/master)

3. **Integration into iteration loop** (lines ~2330-2410):
   - Same worktree lifecycle handling as `ralph_run()`
   - **Fixed**: Now checks return value of `merge_and_close_worktree()` - if merge fails, overrides ticket_rc to 1

## Key Decisions
- **Worktree per ticket**: Chosen to keep parallel runs isolated while preserving merge semantics
- **Always merge on success**: Unlike legacy parallel mode, dispatch backend always merges successful worktrees to integrate changes (by design, not a bug)
- **Config-driven directory**: Uses `parallelWorktreesDir` from config (default: `.tf/ralph/worktrees`)
- **Branch naming**: Uses `ralph/{ticket}` branch format for worktrees

## Fixes Applied (Post-Review)

### Critical Fix
- **Merge failure handling**: Previously, if `merge_and_close_worktree()` returned False (merge conflict/failure), the code still marked the ticket as COMPLETE. Now it properly marks the ticket as FAILED when merge fails.

### Major Fix
- **Deterministic merge target**: Added code to detect the target branch (main/master) and explicitly checkout that branch in repo_root before performing the merge. This prevents merging into whatever branch happens to be checked out.

## Tests Run
- Python syntax check: ✓ `python3 -m py_compile tf/ralph.py`
- Module import: ✓ `from tf.ralph import create_worktree_for_ticket, merge_and_close_worktree, cleanup_worktree`
- Retry state tests: ✓ 60 passed
- Ralph state tests: ✓ 11 passed
- Existing tests: Some pre-existing test failures in `test_ralph_pi_invocation.py` (documented as expected to fail until pt-ihfv)

## Verification
The implementation can be verified by:
1. Running `tf ralph start` with `--dispatch` (default) and observing worktree creation in `.tf/ralph/worktrees/`
2. On successful ticket completion, verify worktree is merged and removed
3. On failed ticket, verify worktree is cleaned up without merge
4. Simulate a merge conflict and verify the ticket is marked as FAILED (not COMPLETE)
5. Check `.tf/ralph/logs/` for worktree operation messages

## Dependencies
- pt-6d99 [closed] - Defines dispatch-default Ralph execution contract
- pt-9yjn [open] - Implements actual dispatch launcher (run_ticket_dispatch)
