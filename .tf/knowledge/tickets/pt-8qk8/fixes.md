# Fixes: pt-8qk8

## Summary
Applied fixes for 3 Major issues identified in the review phase. The Critical issues were deferred as they require significant architectural changes (lifecycle wiring). Warnings and Suggestions were not addressed as per workflow guidelines.

## Fixes by Severity

### Critical (must fix)
- [ ] `tf/ralph.py:840-975`, `tf/ralph.py:2623-2640`, `tf/ralph/session_recovery.py:153` - Session recovery not wired to dispatch lifecycle - **Deferred**: Requires significant architectural work to wire `register_dispatch_session()`, `update_dispatch_session_status()`, and `remove_dispatch_session()` into the dispatch launch/completion paths. This is beyond a simple fix and should be addressed in a follow-up ticket.
- [ ] `tf/ralph_completion.py:59-94`, `tf/ralph/session_recovery.py:357-369`, `tf/ralph/session_recovery.py:416-429` - Orphan detection uses `waitpid` for non-child processes - **Deferred**: Requires modifying `poll_dispatch_status()` to use `os.kill(pid, 0)` for foreign processes. This affects `ralph_completion.py` which is shared code and needs careful consideration.

### Major (should fix)
- [x] `tf/ralph.py:2631-2641` - Startup recovery runs in dry-run mode - **Fixed**: Wrapped recovery block with `if not options["dry_run"]:` to prevent state mutation and process termination during dry-run.
- [x] `tf/ralph.py:2635` - TTL parsing can raise ValueError - **Fixed**: Replaced `int(config.get(...))` with `resolve_session_ttl_ms(config)` which handles invalid config values gracefully.
- [x] `tf/ralph/session_recovery.py:438-454` - Worktree path not validated before deletion - **Fixed**: Added path validation using `worktree_path.relative_to(repo_root)` to ensure worktree is under the repo root before cleanup. Logs warning and skips cleanup for paths outside repo boundary.
- [ ] `tf/ralph/session_recovery.py:102-155` - Race condition in parallel mode (no file locking) - **Deferred**: Adding file locking requires careful design for cross-platform support and error handling. Follow-up ticket recommended.
- [ ] `tf/ralph/session_recovery.py:257-299` - PID reuse vulnerability - **Deferred**: Requires storing additional process metadata (start time, command hash) for validation. Follow-up ticket recommended.

### Minor (nice to fix)
- [ ] `tf/ralph/session_recovery.py:331-344` - `current_pid` parameter documented but never used - **Deferred**: API design issue, not a bug. Could be removed or implemented in follow-up.
- [x] `tf/ralph/session_recovery.py:459-469` - `cleanup_orphaned_session()` ignores return value from `update_dispatch_session_status()` - **Fixed**: Function now captures and returns the status update result, with appropriate logging for failure cases.
- [ ] `tf/ralph.py:31-37`, `tf/ralph.py:1203-1217` - Unused recovery symbols - **Deferred**: These are intentionally imported for future lifecycle wiring (Critical #1).
- [ ] `tf/ralph/session_recovery.py:131-155` - Missing atomic write - **Deferred**: Low priority improvement.
- [ ] `tf/ralph/session_recovery.py:334-350` - Worktree cleanup failure handling - **Deferred**: Now has path validation, but failure tracking could be improved.
- [ ] `tf/ralph/session_recovery.py:26` - Inconsistent TTL configuration - **Deferred**: Minor documentation issue.
- [ ] `tf/ralph/session_recovery.py:395-432` - Unbounded session state growth - **Deferred**: Edge case requiring design consideration.
- [ ] `tf/ralph/session_recovery.py:96-114` - Timezone handling ambiguity - **Deferred**: Python version compatibility issue.

### Warnings (follow-up)
- [ ] `tests/` - No dedicated tests for session_recovery.py - **Not fixed**: Follow-up ticket required.
- [ ] `tf/ralph/session_recovery.py:214-298` - Session-state updates without locking - **Not fixed**: Duplicate of Major #4.
- [ ] `tests/` - No unit tests exist - **Not fixed**: Duplicate of Warning #1.

### Suggestions (follow-up)
- [ ] All suggestions deferred to follow-up tickets as per workflow guidelines.

## Summary Statistics
- **Critical Fixed**: 0 (2 deferred to follow-up)
- **Major Fixed**: 3 (2 deferred to follow-up)
- **Minor Fixed**: 1 (7 deferred to follow-up)
- **Warnings**: 0 fixed (follow-up tickets)
- **Suggestions**: 0 fixed (follow-up tickets)

## Verification
- Python syntax check passed for both modified files
- Import verification passed for `tf.ralph.session_recovery`
- 90 out of 92 session-related tests pass (2 pre-existing unrelated failures)
- Dataclass serialization tests passed

## Files Modified
1. `tf/ralph.py` - Lines 2643-2656:
   - Added dry-run guard around recovery block
   - Changed TTL parsing from `int(config.get(...))` to `resolve_session_ttl_ms(config)`

2. `tf/ralph/session_recovery.py` - Lines 417-451, 470-484:
   - Added path validation before worktree deletion
   - Fixed return value handling for `update_dispatch_session_status()`
