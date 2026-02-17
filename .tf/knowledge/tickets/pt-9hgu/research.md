# Research: pt-9hgu

## Status
Research completed. Lock file lifecycle infrastructure partially exists; needs hardening for guaranteed release and robust error handling.

## Rationale
Research performed to understand current lock implementation state and identify gaps for the lock file lifecycle (acquire, stale recovery, release) requirements.

## Context Reviewed

### Ticket Details (pt-9hgu)
**Title**: Implement /ralph-loop lock file lifecycle (acquire, stale recovery, release)

**Acceptance Criteria**:
- Lock file includes runId/pid/startedAt
- Same runId can continue (re-entrant turns)
- Different live run blocks
- Stale lock replaced (PID liveness detection)
- Lock released on completion/failure

**Blocking**: pt-2rjt, pt-f9cy, pt-rmix  
**External Ref**: ralph-loop-parity

### Current Implementation Analysis (`tf/ralph_loop.py`)

The lock file lifecycle is **partially implemented**:

| Feature | Status | Implementation |
|---------|--------|----------------|
| Lock format (runId/pid/startedAt) | ✅ Done | `write_lock()` writes JSON with all fields |
| Re-entrant turns (same runId) | ✅ Done | `reconcile_lock()` checks `lock["runId"] == run_id` |
| Different live run blocks | ✅ Done | `is_process_alive()` checks PID via `os.kill(pid, 0)` |
| Stale lock replacement | ✅ Done | Dead PID triggers `remove_lock()` + `write_lock()` |
| Lock release on completion | ⚠️ Partial | `remove_lock()` called on completion paths |
| Lock release on failure | ⚠️ Partial | `finally` block exists but is incomplete |

**Identified Gaps**:

1. **Incomplete finally block** (lines 541-556):
   ```python
   finally:
       if lock_acquired:
           if state.get("active"):
               pass  # Keep lock for next turn
           else:
               pass  # No-op - should release lock
   ```
   The finally block has `pass` statements instead of actual lock release logic.

2. **Missing lock release on exception paths**: If an exception occurs after `lock_acquired = True` but before the main completion logic, the lock may not be released.

3. **No signal handler for SIGINT/SIGTERM**: The lock won't be released if the process is killed via signal.

### Related Lessons Learned (from `.tf/ralph/AGENTS.md`)

- **pt-hpme**: Maintain behavioral parity when refactoring - compare implementations for edge cases
- **pt-tupn**: After moving modules, verify imports are fully updated
- **pt-m06z**: mock.patch() paths must match import namespace
- **abc-123**: Use `__main__.py` for CLI entry points to avoid RuntimeWarning

### Blocking Ticket Dependencies

- **pt-rmix** (completion handling): Depends on lock lifecycle being stable
- **pt-2rjt** (worktree lifecycle): Needs lock for safe worktree operations
- **pt-f9cy** (component-safety): Parallel dispatch needs lock coordination

### Existing Lock File Format

Current lock at `.tf/ralph/dispatch-loop.lock`:
```json
{
  "runId": "test-new-run-id",
  "pid": 2400441,
  "startedAt": "2026-02-17T16:14:12Z"
}
```

Also supports legacy space-separated format for backward compatibility.

## Research Findings

### Implementation Requirements

1. **Guaranteed Lock Release**:
   - Use try/finally with proper cleanup
   - Install signal handlers for SIGINT/SIGTERM
   - Ensure `remove_lock()` is called on all exit paths

2. **PID Liveness Detection**:
   - Current `os.kill(pid, 0)` approach is POSIX-compliant
   - Works on Linux/macOS; Windows would need different approach

3. **State Consistency**:
   - Lock file and state file should be kept in sync
   - If lock exists but state is corrupt, should handle gracefully

### Patterns from Stable Ralph (`tf/ralph.py`)

The stable ralph implementation shows signal handling patterns:
```python
def _install_dispatch_signal_handlers() -> None:
    def _handler(signum: int, _frame: Any) -> None:
        _cleanup_dispatch_children()
        raise SystemExit(128 + signum)
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _handler)
```

Similar pattern should be applied to ralph_loop for lock cleanup.

## Sources

1. `tk show pt-9hgu` - Ticket specification
2. `tf/ralph_loop.py` - Current implementation (lines 1-560)
3. `.tf/ralph/AGENTS.md` - Lessons learned
4. `.tf/ralph/dispatch-loop.lock` - Current lock file state
5. `tf/ralph.py` - Signal handling patterns from stable ralph
6. Blocking tickets: pt-rmix, pt-2rjt, pt-f9cy
