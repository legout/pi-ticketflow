# Fixes: pt-9hgu

## Summary
Fixed critical concurrency/safety issues in lock file lifecycle implementation. The fixes were already partially applied from a prior session; this fix phase verified the changes and addressed remaining issues.

## Fixes by Severity

### Critical (must fix)
- [x] `tf/ralph_loop.py:200-217` - **Non-atomic lock acquisition / TOCTOU race**
  - Changed `write_lock()` to use atomic creation via `os.O_CREAT | os.O_EXCL`
  - Returns `False` if lock already exists, allowing caller to reconcile
  - Prevents race condition where two processes could both believe they acquired the lock

- [x] `tf/ralph_loop.py:61-88` - **Signal-handler lock unlink lacks ownership verification**
  - Added `_current_run_id` global for ownership tracking
  - Signal handler now re-reads lock file and verifies `runId` and `pid` match before unlinking
  - Prevents removing a lock owned by a different process/run after ownership change

- [x] `tf/ralph_loop.py:238-261` - **PID reuse vulnerability**
  - Added `get_process_start_time()` function to capture process start time from `/proc/self/stat`
  - Lock file now includes `processStartTime` field for identity verification
  - `is_process_alive()` enhanced to verify process start time when checking liveness
  - Protects against false "alive" detection when PID is reused by a new process

- [x] `tf/ralph_loop.py:284-287` - **Signal timing window**
  - Signal handlers are now installed BEFORE any lock acquisition attempt
  - Cleanup context (`_lock_path_for_cleanup`, `_current_run_id`) is set before lock is written
  - Eliminates window where signal could arrive without proper cleanup state

### Major (should fix)
- [x] `tf/ralph_loop.py:56-64` - **Signal handler re-entrancy protection**
  - Added `_in_signal_handler` global flag
  - Signal handler checks flag on entry, sets it, and uses try/finally to ensure cleanup
  - Prevents undefined behavior from nested signal delivery

- [x] `tf/ralph_loop.py:97-102` - **Re-entrant path refresh**
  - `_install_signal_handlers()` now always updates cleanup context before checking if installed
  - Ensures `_lock_path_for_cleanup` and `_current_run_id` are fresh on re-entrant turns

- [x] `tf/ralph_loop.py:945-949` - **Exception path lock release safety**
  - `finally` block only releases lock if `state.get("active")` is empty
  - Prevents releasing lock while sessions are still in-flight

- [ ] `tf/ralph_loop.py` - **Missing targeted automated tests**
  - Not addressed in this fix phase (requires dedicated test development)
  - Follow-up recommended for regression coverage

### Minor (nice to fix)
- [x] `tf/ralph_loop.py:583-595` - **Dead code removal**
  - Removed unused `command` variable in `launch_dispatch()`

- [x] `tf/ralph_loop.py:318-329` - **Improved stale-lock diagnostics**
  - Error messages now include `started:` timestamp for active locks
  - Stale lock cleanup messages include age information

### Warnings (follow-up)
- [ ] Policy question: fail-open lock release on unexpected exceptions may allow overlapping orchestrators
- [ ] No lock heartbeat/timeout for hung-but-alive owners
- [ ] Session-id short UUID collision risk in tracking path

### Suggestions (follow-up)
- [ ] Consider `flock()` for stronger mutual exclusion on POSIX
- [ ] Add heartbeat/touch mechanism to lock file
- [ ] Add metrics/logging for lock contention time

## Summary Statistics
- **Critical**: 4 (all fixed)
- **Major**: 4 (3 fixed, 1 deferred to follow-up)
- **Minor**: 2 (all fixed)
- **Warnings**: 3 (deferred to follow-up)
- **Suggestions**: 3 (deferred to follow-up)

## Verification
- ✅ Syntax check: `python -m py_compile tf/ralph_loop.py` passed
- ✅ Import test: `from tf import ralph_loop` successful
- ✅ All functions available and accessible
- ✅ Existing tests: `test_ralph_state.py` - 11 passed

## Key Changes Summary

| Issue | Fix | Status |
|-------|-----|--------|
| TOCTOU race in lock acquisition | Atomic O_CREAT|O_EXCL | ✅ |
| Signal handler ownership verification | Verify runId+pid before unlink | ✅ |
| PID reuse vulnerability | Process start time in lock | ✅ |
| Signal timing window | Install handlers before lock | ✅ |
| Signal re-entrancy | Flag-based protection | ✅ |
| Exception path lock safety | Only release if no active sessions | ✅ |
| Re-entrant path refresh | Always update cleanup context | ✅ |
| Dead code | Removed unused variable | ✅ |
| Diagnostics | Added timestamp to messages | ✅ |
| Test coverage | Deferred to follow-up | ⏳ |
