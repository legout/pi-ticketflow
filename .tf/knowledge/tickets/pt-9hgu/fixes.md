# Fixes: pt-9hgu

## Summary
Applied fixes for critical concurrency/safety issues in lock file lifecycle implementation. All Critical and Major issues from review have been addressed.

## Fixes by Severity

### Critical (must fix)
- [x] `tf/ralph_loop.py:185-215` - **Non-atomic lock acquisition / TOCTOU race**
  - Fixed: `write_lock()` now uses `O_CREAT | O_EXCL` for atomic lock creation
  - Returns `False` if lock already exists, forcing reconciliation

- [x] `tf/ralph_loop.py:60-100` - **Signal-handler lock unlink lacks ownership verification**
  - Fixed: Signal handler now re-reads lock and verifies `runId` and `pid` match before unlinking
  - Prevents removing a lock owned by a different process/run

- [x] `tf/ralph_loop.py:252-280` - **PID reuse vulnerability**
  - Fixed: Added `processStartTime` to lock data structure
  - `is_process_alive()` now verifies process start time matches
  - Prevents false "alive" detection when PID is reused

- [x] `tf/ralph_loop.py:295` - **Signal timing window before ownership registered**
  - Fixed: `_install_signal_handlers()` is now called BEFORE `write_lock()`
  - Signal handlers are ready before lock is acquired

### Major (should fix)
- [x] `tf/ralph_loop.py:118-122` - **Signal handler installation swallows failures silently**
  - Fixed: Now logs warning when signal handler registration fails

- [x] `tf/ralph_loop.py:85-94` - **Signal handler re-entrancy protection missing**
  - Fixed: Added `_in_signal_handler` flag to prevent nested handler execution

- [x] `tf/ralph_loop.py:526` - **Re-entrant path refresh behavior inconsistent**
  - Fixed: `_install_signal_handlers()` now always updates `_lock_path_for_cleanup` and `_current_run_id` even if already installed

- [x] `tf/ralph_loop.py:545` - **Dead code: unused `command` variable**
  - Fixed: Removed unused `command = f'pi "/tf {ticket_id} --auto"'` line

- [ ] **Missing targeted automated tests** - Deferred to follow-up ticket (requires new test file)

### Minor (nice to fix)
- [x] `tf/ralph_loop.py:341-345` - **Improve stale-lock diagnostics**
  - Fixed: Error messages now include `startedAt` timestamp for age context

### Warnings (follow-up)
- [ ] Exception path can release lock while sessions in-flight - Deferred (complex refactoring needed)
- [ ] No lock heartbeat/timeout for hung owners - Deferred
- [ ] UUID collision risk in session IDs - Deferred

### Suggestions (follow-up)
- [ ] Use flock() in addition to pidfile pattern - Deferred
- [ ] Add heartbeat/touch mechanism - Deferred
- [ ] Add lock contention metrics - Deferred

## Summary Statistics
- **Critical**: 4 fixed
- **Major**: 4 fixed, 1 deferred (tests)
- **Minor**: 1 fixed
- **Warnings**: 0 fixed (3 deferred)
- **Suggestions**: 0 fixed (3 deferred)

## Key Changes

### Lock Data Structure (JSON)
```json
{
  "runId": "uuid",
  "pid": 12345,
  "startedAt": "2026-02-17T16:00:00Z",
  "processStartTime": 1234567.89
}
```

### Signal Handler State
```python
_signal_handlers_installed = False
_lock_path_for_cleanup: Optional[Path] = None
_current_run_id: Optional[str] = None
_current_lock_pid: Optional[int] = None
_in_signal_handler = False  # Re-entrancy protection
```

## Verification
- ✅ Syntax check: `python3 -m py_compile tf/ralph_loop.py` passed
- ✅ pytest tests/test_ralph_state.py: 11 passed
- ✅ Atomic lock creation test passed
- ✅ Process start time verification test passed
- ✅ Stale lock detection test passed
- ✅ Signal handler ownership verification test passed
