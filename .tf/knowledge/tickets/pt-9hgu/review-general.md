# Review: pt-9hgu

## Overall Assessment
The lock-file schema and stale-lock detection logic are thoughtfully implemented, especially around atomic create and PID/start-time checks. However, the surrounding dispatch/session tracking has a correctness gap that can mark work as successful without evidence, which undermines loop correctness and lock lifecycle guarantees in real runs. There is also a lock-release race window that can remove another process’s lock.

## Critical (must fix)
- `tf/ralph_loop.py:620-623`, `tf/ralph_loop.py:580-583` - `launch_dispatch()` stores a synthetic UUID fragment instead of the real session id, and `query_session_status()` treats “id not found” as completion/success. This can produce false completions and success reporting for tickets that are still running or failed, which can prematurely drain `active` and allow terminal cleanup paths to run incorrectly.

## Major (should fix)
- `tf/ralph_loop.py:965-977`, `tf/ralph_loop.py:1005-1007`, `tf/ralph_loop.py:274-281` - lock removal is done in completion branches and again in `finally`, and `remove_lock()` does not verify ownership. A second process can acquire the lock between those two removals, after which the first process may unlink the new owner’s lock.
- `tf/ralph_loop.py:587-589` - on any exception while checking background status, code returns `{"finished": True, "success": True}`. Operational failures in status checks are silently converted into success, hiding real errors and skewing state (`completed` vs `failed`).

## Minor (nice to fix)
- `tf/ralph_loop.py:36` - `_current_lock_pid` is defined but unused, which adds dead state and makes lock-ownership intent less clear.
- `tf/ralph_loop.py:437-448` - `backup_corrupt_state()` is currently unused. This increases maintenance surface and suggests intended corruption handling is incomplete.

## Warnings (follow-up ticket)
- `tf/ralph_loop.py:202-402`, `tf/ralph_loop.py:558-627`, `tf/ralph_loop.py:860-1007`, `tests/test_ralph_state.py:1` - there is no direct automated coverage for `ralph_loop` lock/session lifecycle (existing referenced tests target `tf.ralph.update_state`). Regression risk is high for race-sensitive behavior and failure-mode handling.

## Suggestions (follow-up ticket)
- `tf/ralph_loop.py:592-627` - plumb and persist the actual dispatch/background session id from `pi` output (or switch to a machine-readable output mode) and make `query_session_status()` authoritative against that id.
- `tf/ralph_loop.py:274-281`, `tf/ralph_loop.py:1000-1007` - add ownership-checked unlock (`runId` + `pid` + optional `processStartTime`) and clear `lock_acquired` after explicit unlock to avoid double-unlink races.

## Positive Notes
- `tf/ralph_loop.py:242-271` uses atomic lock creation (`O_CREAT | O_EXCL`), which is the right primitive for cross-process coordination.
- `tf/ralph_loop.py:304-334` includes PID reuse protection via process start-time validation, reducing stale-PID false positives.
- `tf/ralph_loop.py:60-95` signal handler attempts ownership verification before cleanup, a solid safety-oriented design choice.

## Summary Statistics
- Critical: 1
- Major: 2
- Minor: 2
- Warnings: 1
- Suggestions: 2
