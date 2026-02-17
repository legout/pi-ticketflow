# Review: pt-4eor
## Overall Assessment
The dispatch integration in the serial loop is close, but there are two lifecycle gaps that can leave internal dispatch bookkeeping inconsistent after ticket completion. The main flow now waits for dispatch completion and updates ticket state, which is good, but process/session cleanup parity with the parallel path is incomplete. I also found one diagnostics regression that makes failures harder to triage.

## Critical (must fix)
- `tf/ralph.py:157-159,959,2848-2872` - Dispatch child PIDs are registered (`_register_dispatch_child`) but never unregistered in the serial wait path after completion. Because signal handlers later iterate `_dispatch_child_pids` and call `_terminate_process_group` on each remembered PID, stale entries can target unrelated process groups if PID reuse occurs, causing unintended process termination on Ctrl+C/SIGTERM.

## Major (should fix)
- `tf/ralph.py:976-987,2824-2872` - Serial dispatch runs register sessions in `dispatch-sessions.json` as `running`, but this path never calls `update_dispatch_session_status(...)` on completion/failure (unlike parallel mode at `tf/ralph.py:3180-3201`). This leaves completed serial sessions permanently marked `running`, which breaks state accuracy and forces startup recovery to treat finished work as orphan cleanup candidates.

## Minor (nice to fix)
- `tf/ralph.py:2841-2843,2965-2974` - When dispatch launch fails, the specific launch error is logged once but later collapsed into a generic `pi -p failed (exit 1)` state/error message. This drops actionable context from progress artifacts and makes debugging retries harder.

## Warnings (follow-up ticket)
- `.tf/knowledge/tickets/pt-4eor/implementation.md:22-35` - The implementation artifact reports `pytest -v` failing during collection (`tests/test_post_fix_verification.py`), so regression confidence for this change set is currently incomplete.

## Suggestions (follow-up ticket)
- `tf/ralph.py:2822-2872` - Add focused tests for serial dispatch lifecycle parity with parallel mode: (1) session status transitions to terminal state, and (2) registered child PID is removed after completion/timeout/failure.

## Summary Statistics
- Critical: 1
- Major: 1
- Minor: 1
- Warnings: 1
- Suggestions: 1
