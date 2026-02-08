# Implementation: pt-j485 - Ensure cleanup semantics after timeout

## Summary
Implemented safety checks to ensure proper cleanup semantics after timeout by preventing parallel mode execution when timeout/restart settings are configured.

## Changes Made

### 1. Parallel Mode Safety Check (tf_cli/ralph.py)
Added a safety check in `ralph_start()` that detects when timeout (`attemptTimeoutMs > 0`) or restart (`maxRestarts > 0`) settings are configured alongside parallel mode (`use_parallel > 1`). When this unsafe combination is detected:
- A warning is logged explaining why parallel mode is being disabled
- Execution falls back to serial mode for safe cleanup semantics

```python
# Safety check: timeout/restart is not supported in parallel mode
# Per constraint: prefer warn+disable over partial/unsafe behavior
timeout_ms = resolve_attempt_timeout_ms(config)
max_restarts = resolve_max_restarts(config)
if use_parallel > 1 and (timeout_ms > 0 or max_restarts > 0):
    logger.warn(
        f"Timeout ({timeout_ms}ms) and restart ({max_restarts}) settings are not supported in parallel mode. "
        "Falling back to serial mode for safe cleanup semantics."
    )
    use_parallel = 1
```

### 2. Documentation Updates
- Updated DEFAULTS dict comments to indicate "Serial mode only" for `attemptTimeoutMs` and `maxRestarts`
- Updated usage() text to clarify these settings only work in serial mode

### 3. Code Organization
- Moved timeout/restart resolution earlier in the function (before the parallel mode check)
- Removed duplicate resolution that was inside the `try` block

## Rationale

Per the ticket constraint: "Prefer warn+disable in parallel mode over partial/unsafe behavior"

The parallel mode implementation uses `subprocess.Popen` without timeout handling. Adding timeout support to parallel mode would require:
1. Thread-based timeout monitoring for multiple concurrent processes
2. Safe termination of worktree-based subprocesses
3. Cleanup of dangling worktrees on timeout
4. Restart logic that coordinates across parallel workers

This complexity introduces risk of partial cleanup (leaving worktrees, locks, or zombie processes). The safer approach is to warn the user and fall back to serial mode, where timeout/restart is fully implemented and tested.

## Verification

The implementation ensures:
1. ✓ Lock handling remains correct (lock released in `finally` block)
2. ✓ Progress/state files reflect timeout outcome (via `update_state()`)
3. ✓ Parallel mode does not regress (warns and falls back to serial)
4. ✓ No dangling worktrees from timeout (serial mode handles cleanup)

## Files Changed
- `tf_cli/ralph.py` - Added parallel mode safety check, updated documentation
