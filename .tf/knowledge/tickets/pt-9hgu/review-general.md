# Review: pt-9hgu

## Overall Assessment
The lock lifecycle work improves reliability (signal cleanup + safer `finally` state handling), but there are still correctness gaps that can break mutual exclusion in real contention scenarios. The largest risk is that lock acquisition is still non-atomic, so two concurrent loop starts can both proceed as owners.

## Critical (must fix)
- `tf/ralph_loop.py:196-201` and `tf/ralph_loop.py:222-223` - Lock acquisition/replacement is a read-then-write sequence (`read_lock` → `write_lock`) without atomic create semantics. Two processes can race and both believe they acquired the lock, which violates the core single-owner guarantee.
- `tf/ralph_loop.py:140-141`, `tf/ralph_loop.py:204`, `tf/ralph_loop.py:210` - JSON lock contents are not schema-validated before keyed access. A malformed lock (missing keys or non-int `pid`) raises `KeyError`/`TypeError` and crashes reconciliation instead of recovering cleanly, potentially leaving the loop unusable until manual intervention.

## Major (should fix)
- `tf/ralph_loop.py:56-64` - Signal cleanup unconditionally unlinks the lock path without verifying ownership (`runId`/`pid`). In edge cases, this can delete a lock written by another process and allow overlap.
- `tf/ralph_loop.py:813-818` - Exception path always calls `remove_lock(ralph_dir)` when `lock_acquired`, even if active sessions are still running. That can allow a new loop instance to start while prior dispatches are in flight.
- `tests/test_bundle_manifest.py:12-29` - Current tests only verify prompt/config wiring; there is no automated coverage for `reconcile_lock`, stale-lock replacement, malformed lock recovery, or signal-triggered cleanup. Regressions in lock behavior are likely to go undetected.

## Minor (nice to fix)
- `tf/ralph_loop.py:75-79` - `_install_signal_handlers()` returns early once installed and does not refresh `_lock_path_for_cleanup`. The re-entrant install calls are therefore misleading in long-lived in-process usage.

## Warnings (follow-up ticket)
- `tf/ralph_loop.py:178-184` and `tf/ralph_loop.py:210` - PID liveness check uses only `os.kill(pid, 0)`. PID reuse can misclassify an unrelated process as the lock owner, causing false blocking.

## Suggestions (follow-up ticket)
- `tf/ralph_loop.py:156-165` and `tf/ralph_loop.py:187-225` - Use atomic lock creation (`os.open(..., O_CREAT|O_EXCL)`) and atomic stale-lock handoff logic to remove TOCTOU windows.
- `tf/ralph_loop.py:127-153` and `tf/ralph_loop.py:187-225` - Add strict lock schema validation (`runId: str`, `pid: int`, `startedAt: str`) and fallback behavior for corrupted lock files (e.g., quarantine + replace).

## Positive Notes
- Good move to initialize `state` as optional and guard `finally` access.
- Lock metadata format (`runId`/`pid`/`startedAt`) is clear and extensible.
- Logging around stale-lock cleanup and lifecycle events is readable and operationally useful.

## Summary Statistics
- Critical: 2
- Major: 3
- Minor: 1
- Warnings: 1
- Suggestions: 2
