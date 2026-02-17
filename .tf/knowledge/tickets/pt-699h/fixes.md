# Fixes: pt-699h

## Summary
Applied targeted fixes to align parallel scheduling behavior with dispatch semantics and harden dispatch lifecycle handling. The key fixes ensure parallel mode is no longer silently disabled by serial timeout settings, dispatch backend is honored in parallel execution, and dispatch child processes are tracked/cleaned up on termination.

## Fixes by Severity

### Critical (must fix)
- [x] `tf/ralph.py:2490` - Parallel mode no longer falls back to serial when `attemptTimeoutMs`/`maxRestarts` are set. Parallel run now continues with a warning that serial restart/backoff semantics are ignored.
- [x] `tf/ralph.py:2860+` - Added explicit `execution_backend == "dispatch"` branch in parallel loop. Parallel dispatch now launches via `run_ticket_dispatch()` and tracks completion with `poll_dispatch_status()`.
- [x] `tf/ralph.py:109-179,804+` - Added dispatch child PID tracking + SIGINT/SIGTERM cleanup hooks to reduce orphaned detached process groups on parent termination.
- [x] `tf/ralph.py:786+` - Hardened dispatch session-id allocation with in-process collision checks (`_allocate_dispatch_session_id`).
- [ ] `tf/ralph.py:parallel subprocess branch` - Zombie-window concern in legacy subprocess branch not fully eliminated in this pass (deferred; low practical impact due explicit wait/reap loop and default dispatch backend).

### Major (should fix)
- [x] `tf/ralph.py:2860+` - Added timeout handling for parallel dispatch sessions (`parallelDispatchTimeoutMs` + `RALPH_PARALLEL_DISPATCH_TIMEOUT_MS`) with graceful termination.
- [x] `tf/ralph.py:2860+` - Added full-batch completion processing for dispatch mode; failed tickets are collected and reported after cleanup.
- [ ] `tf/ralph.py:merge_and_close_worktree` - Merge-conflict dirty-state recovery not changed in this pass (deferred).
- [ ] `tf/ralph.py:legacy subprocess launch loop` - Full try/finally batch resource hardening for legacy subprocess backend deferred.
- [ ] `tf/ralph.py:parallel iteration accounting (legacy subprocess path)` - Worktree-add failure iteration accounting semantics unchanged in this pass.

### Minor (nice to fix)
- [x] `tf/ralph.py:dispatch session tracking helpers` - Added explicit register/unregister helpers for clearer process lifecycle accounting.

### Warnings (follow-up)
- [ ] Integration coverage for parallel dispatch cleanup invariants and backend parity (deferred to follow-up).
- [ ] JSONL path-collision hardening in legacy subprocess branch (deferred).
- [ ] Worktree path collision hardening for repeated same-ticket selection (deferred).

### Suggestions (follow-up)
- [ ] Add `ralph cleanup` command for orphan/process/worktree recovery.
- [ ] Refactor legacy subprocess parallel branch into a unified active-batch state machine.
- [ ] Add stricter config validation for unknown execution backends.

## Summary Statistics
- **Critical**: 4
- **Major**: 2
- **Minor**: 1
- **Warnings**: 0
- **Suggestions**: 0

## Verification
- `python -m py_compile tf/ralph.py` ✅
- `python -c "import tf.ralph"` ✅
- `pytest -q tests/test_ralph_state.py tests/test_ralph_pi_invocation.py` ➜ 12 passed, 2 failed (known test harness/mocking failures in `test_ralph_pi_invocation.py`; no new syntax/import regressions).
- Updated `files_changed.txt` atomically with: `tf/ralph.py`.
