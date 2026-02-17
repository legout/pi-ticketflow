# Review: pt-9hgu

## Critical (must fix)
- `tf/ralph_loop.py:196-201,222-223` - Lock acquisition/replacement is non-atomic (read-then-write), so concurrent starters can both believe they hold the lock (TOCTOU race).
- `tf/ralph_loop.py:140-141,204,210` - Lock JSON is not schema-validated before keyed access; malformed lock content can crash reconciliation instead of recovering.
- `tf/ralph_loop.py:33-42,56-64` - Signal-path cleanup can unlink lock files without strict ownership verification (`runId`/`pid`), risking deletion of another run’s lock.
- `tf/ralph_loop.py:163-169,178-184` - PID liveness check (`os.kill(pid, 0)`) is vulnerable to PID reuse, which can falsely classify stale locks as live.

## Major (should fix)
- `tf/ralph_loop.py:813-818` - Exception-path cleanup removes lock whenever `lock_acquired` is true, even if active sessions may still be in flight.
- `tests/test_bundle_manifest.py:12-29` - No targeted automated coverage for lock lifecycle edge cases (stale lock replacement, malformed locks, signal-triggered cleanup, contention races).
- `tf/ralph_loop.py:378-390` - `completed` / `failed` lists can grow without bound in long-running loops.
- `tf/ralph_loop.py:207-216` - State save uses temp+rename but does not fsync before rename; crash consistency could be improved.
- `tf/ralph_loop.py:319-322` - Generated short UUID session IDs may not correspond to real `pi` session IDs, causing status tracking inaccuracies.

## Minor (nice to fix)
- `tf/ralph_loop.py:75-79` - `_install_signal_handlers()` early-return behavior can make re-entrant refresh calls misleading (cleanup context/path may not be refreshed as expected).

## Warnings (follow-up ticket)
- None.

## Suggestions (follow-up ticket)
- `tf/ralph_loop.py:156-165,187-225` - Switch to atomic lock creation/handoff (`O_CREAT|O_EXCL` or `flock`/`lockf`) to fully close contention windows.
- `tf/ralph_loop.py:127-153,187-225` - Add strict lock-schema validation with quarantine/rewrite behavior for corrupt lock files.

## Summary Statistics
- Critical: 4
- Major: 5
- Minor: 1
- Warnings: 0
- Suggestions: 2

## Notes
- `review-spec.md` reported no spec-compliance gaps and acceptance-criteria alignment.
- Consolidation deduplicated overlapping findings from `review-general.md` and `review-second.md` by keeping highest severity.
