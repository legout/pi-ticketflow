# Review: pt-ussr

## Overall Assessment
The implementation correctly displays ready/blocked counts in TTY and non-TTY modes. However, several edge cases around negative counts, queue state computation timing, stale tracking, and data type consistency could cause subtle bugs or confusing behavior.

## Critical (must fix)

### tf/ralph/queue_state.py:72-79 - No validation for negative counts in QueueStateSnapshot
`__post_init__` only validates that total equals sum of states but doesn't ensure counts are non-negative. If `len(pending) < blocked_count` (e.g., bug in caller or corrupted dep_graph), `ready_count` becomes negative. This creates invalid state that passes validation.

**Impact**: Negative counts in progress display and logs (e.g., "R:-2 B:5") causing user confusion and potentially breaking downstream parsing.

**Suggested fix**: Add validation: `if any(x < 0 for x in (self.ready, self.blocked, self.running, self.done)): raise ValueError(...)`.

### tf/ralph.py:814-823 - Queue state not recomputed during timeout retry loops
When a ticket times out and restarts (lines 864-877 in `ralph_start`), the queue state snapshot captured before ticket processing (line 820) remains unchanged across retry attempts. Blocked tickets may have become ready during retry attempts, but the displayed counts remain stale.

**Impact**: Progress display and logs show outdated ready/blocked counts during extended retry sequences, misleading users about actual queue state.

**Suggested fix**: Recompute queue state after each failed attempt before retry, or document that counts are only accurate at ticket boundaries.

### tf/ralph.py:1604-1612 - _last_line_len is tracked but never used
`ProgressDisplay._last_line_len` is initialized to 0 and never updated or read. This appears to be dead code from an earlier design (possibly for clearing partial lines in non-TTY mode).

**Impact**: Dead code suggests incomplete implementation; future developers may rely on non-existent behavior.

**Suggested fix**: Either remove `_last_line_len` or implement the intended tracking logic if this is a gap in the implementation.

## Major (should fix)

### tf/ralph.py:805-823 - No handling for stale ready_ids/blocked_ids when ticket is already running
The queue state computation assumes `ready_ids | blocked_ids` equals all pending tickets. However, if the selected ticket was in `ready_ids` (it should be), marking it as `running_ticket` and computing snapshot doesn't account for the fact that the ticket may have already moved from ready to running between listing and selection.

**Impact**: In rare race conditions, the selected ticket could be counted twice (once in ready_ids, once in running_ids), inflating the total count by 1.

**Suggested fix**: Remove selected ticket from `pending_ids` before computing snapshot: `pending_ids = (ready_ids | blocked_ids) - {ticket}`.

### tf/ralph.py:287-293 - Timestamp inconsistency: progress uses local time, logger uses UTC
`ProgressDisplay._draw()` uses `datetime.now()` (local time) for timestamps, while `RalphLogger._utc_now()` uses UTC. Logs from both sources are difficult to correlate when working across time zones.

**Impact**: Confusing log analysis; timestamps from progress output and logger don't align, complicating debugging.

**Suggested fix**: Use UTC consistently in `ProgressDisplay` as well: `datetime.now(timezone.utc).strftime("%H:%M:%S")`.

### tf/ralph.py:268-276 - Non-TTY mode silent during long-running tickets
Comment explicitly states "In non-TTY mode, we don't show intermediate progress to avoid spam." However, for long-running tickets (e.g., 10+ minutes), users may think Ralph is stuck with no output.

**Impact**: Users may prematurely terminate long-running tickets due to lack of feedback; poor UX in batch processing scenarios.

**Suggested fix**: Consider adding heartbeat output in non-TTY mode (e.g., every 60 seconds of processing) or document this behavior prominently.

### tf/ralph/queue_state.py:128-133 - Silent failure on shell command errors in _refresh_pending_state
When `tk ready` or `tk blocked` fail, the function catches exceptions and returns empty sets without logging the failure. This masks infrastructure issues (e.g., tk not in PATH).

**Impact**: Silent failures cause queue state to show 0 ready/0 blocked even when tickets exist. Users see incorrect progress and logs.

**Suggested fix**: Log warnings before returning empty sets: `logger.warn(f"Failed to list ready tickets: {exc}")`.

## Minor (nice to fix)

### tf/logger.py:225-229 - queue_state logged twice in log_ticket_start
When `queue_state` is provided, the function adds it both as a structured field (`extra["queue_state"]`) and embedded in the message (`[{queue_state.to_log_format()}]`). This is redundant and increases log verbosity.

**Impact**: Log lines are longer than necessary; redundant information in structured vs. human-readable parts.

**Suggested fix**: Either remove the embedded message format or the structured field, not both.

### tf/ralph.py:822-823 - Sentinel value __unmet_dependency__ could cause issues if ticket ID matches
The sentinel `_BLOCKED_DEP_SENTINEL = "__unmet_dependency__"` is used as a fake dependency to mark blocked tickets. If a real ticket ID is `__unmet_dependency__`, the sentinel approach breaks (though highly unlikely).

**Impact**: In the extremely unlikely event of a ticket with this exact ID, blocked counting logic would incorrectly classify it.

**Suggested fix**: Use a more distinct sentinel like `_BLOCKED_DEP_SENTINEL = "\0__BLOCKED_SENTINEL__\0"` or UUID.

### tf/ralph.py:273 - TTY mode double-newline on completion
In `ProgressDisplay._draw()` with `final=True` in TTY mode, the output is `\x1b[2K\r{timestamp} {message}\n`. After the previous `\r` from `start_ticket`, this creates two visual lines. The intention is to finalize the progress line, but the visual result is a blank line before the completion message.

**Impact**: Slightly verbose output; each completion creates a blank line visually (though not in log files).

**Suggested fix**: Consider whether the blank line is intended; if not, adjust TTY clearing logic.

## Warnings (follow-up ticket)

### tf/ralph/queue_state.py:105-116 - No overflow protection for large queues
QueueStateSnapshot uses Python `int` which has arbitrary precision, so overflow isn't a concern. However, extremely large queues (millions of tickets) could cause performance issues in counting operations.

**Impact**: At extreme scale, the O(|pending| + |running| + |completed|) complexity could cause noticeable delays between tickets.

**Deferred risk**: Only relevant for enterprise-scale deployments; not urgent for typical use cases.

### tf/ralph.py:798-823 - Queue state computation happens twice per iteration (start + complete)
The queue state is computed twice: once before ticket starts and once after it completes. For very large queues, this doubles the overhead per ticket.

**Impact**: Performance impact at scale; redundant computation if queue state hasn't changed during ticket processing.

**Deferred risk**: Minor performance concern; consider caching or deferring recompute only when needed.

### tf/ralph.py:820 - No queue state parameter in parallel mode
The parallel mode code path does not compute or display queue state (no `ProgressDisplay` in parallel mode). This means ready/blocked counts are only available in serial mode.

**Impact**: Users in parallel mode miss queue visibility that serial mode provides.

**Deferred risk**: Per design (--progress only works in serial mode), but could be a gap for future parallel progress indicators.

## Suggestions (follow-up ticket)

### tf/ralph/queue_state.py:87 - Consider adding __repr__ for debugging
`QueueStateSnapshot` has `__str__` for display and `to_log_format` for logging, but no `__repr__` for debugging in REPL or error messages.

**Optional improvement**: Add `def __repr__(self) -> str: return f"QueueStateSnapshot(ready={self.ready}, blocked={self.blocked}, ...)"` to aid debugging.

### tf/logger.py:422-428 - Log level for loop completion could be INFO instead of WARN for "max_iterations_reached"
When loop completes due to `max_iterations_reached`, level is INFO, but when `backlog_empty`, it's also INFO. However, other conditions might use WARN in the future.

**Optional improvement**: Consider whether `max_iterations_reached` should be WARN (possible incomplete work) vs INFO (normal termination). Currently both are INFO, which is fine but could be documented.

### tf/ralph.py:296 - TTY control sequence handling could use a helper class
The TTY-specific escape sequences (`\x1b[2K\r`) are embedded directly in `_draw()`. For future TTY features (colors, cursor movement), this could become messy.

**Optional improvement**: Extract to a `TTYFormatter` class for cleaner separation of concerns.

## Positive Notes

- **Immutable snapshot design**: `QueueStateSnapshot` as frozen dataclass with invariant validation is a solid choice for thread-safe state reporting.
- **Comprehensive test coverage**: The 74 tests across three test files demonstrate good coverage of TTY/non-TTY behavior and queue state computation.
- **Clean separation of concerns**: Progress display, logging, and queue state computation are well-separated with clear interfaces.
- **Graceful degradation**: Non-TTY mode correctly omits control characters, ensuring log parsing safety.

## Summary Statistics
- Critical: 3
- Major: 5
- Minor: 3
- Warnings: 3
- Suggestions: 3
