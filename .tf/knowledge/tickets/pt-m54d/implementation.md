# Implementation: pt-m54d - Ralph Ready/Blocked Semantics + Output Contract

## Summary
Defined queue-state semantics (ready/blocked/running/done) and output format specifications for Ralph progress display and logging. This specification unblocks downstream implementation tickets (pt-oa8n, pt-ussr).

## State Semantics Definitions

### Queue States

| State | Definition | MVP Scope |
|-------|------------|-----------|
| **Ready** | Tickets that are runnable but not currently being processed | Yes - count of tickets returned by `tk ready` minus any currently running |
| **Blocked** | Tickets that cannot run due to unmet dependencies | Yes - deps-only for MVP |
| **Running** | Ticket(s) currently being processed by Ralph | Yes - tracked in-memory by scheduler |
| **Done** | Tickets completed (success or failure) during current run | Yes - cumulative count since loop start |
| **Total** | Sum of ready + blocked + running + done | Yes - derived from known ticket set |

### Key Invariants

1. **Ready Exclusion**: Running ticket is **never** counted in ready
   - When a ticket starts: ready -= 1, running += 1
   - When a ticket completes: running -= 1, done += 1

2. **Blocked Definition (MVP)**: Only unmet dependencies count as blocked
   - Other blocking reasons (component locks, filters, failures) are out of scope
   - A ticket with deps that are all "done" is ready, not blocked

3. **Count Accuracy**: Counts are derived from in-memory scheduler state
   - No external `tk` calls required after initial load
   - Updates happen at state transitions (start/complete/fail)

4. **Serial vs Parallel**: Counts work for both modes
   - Serial: max 1 running ticket
   - Parallel: up to N running tickets (where N = parallel workers)

## Output Format Specification

### Display Format

```
R:{ready} B:{blocked} (done {done}/{total})
```

**Examples:**
- `R:3 B:2 (done 1/6)` - 3 ready, 2 blocked, 1 done of 6 total
- `R:0 B:5 (done 0/5)` - Nothing ready, 5 blocked (waiting on external deps)
- `R:5 B:0 (done 0/5)` - All tickets ready, no blockers

### TTY Mode Output

**Progress Line (in-place updates):**
```
14:32:05 [1/6] Processing pt-abc123...  R:3 B:2 (done 0/6)
14:32:15 [1/6] ✓ pt-abc123 complete     R:2 B:2 (done 1/6)
```

- Uses carriage return (`\r`) + clear line (`\x1b[2K`) for in-place updates
- Timestamp prefix in `HH:MM:SS` format
- Queue state appended to progress line

### Non-TTY Mode Output

**Log Lines (no control characters):**
```
14:32:05 Starting ticket pt-abc123 [R:3 B:2 done:0/6]
14:32:15 Completed ticket pt-abc123 [R:2 B:2 done:1/6]
```

- No animated control characters
- Same information, different format
- One line per event (start/complete)

### Normal Logging (Non-Progress Mode)

When `--progress` is not enabled, counts are logged at ticket boundaries:

```
[ralph] Starting ticket pt-abc123 (R:3 B:2 done:0/6)
[ralph] Completed ticket pt-abc123 status=COMPLETE (R:2 B:2 done:1/6)
```

## Backwards Compatibility Strategy

### Recommended Approach: Flag-Gated

Add a configuration option to control the new format:

```json
// .tf/ralph/config.json
{
  "showQueueState": true  // Enable new format (default: false for compat)
}
```

**Rationale:**
- Current `[iteration/total]` format may be parsed by scripts
- Sudden format changes break existing tooling
- Flag allows opt-in migration

### Migration Path

1. **Phase 1 (Current)**: Flag defaults to `false`, old format only
2. **Phase 2 (Future)**: Flag defaults to `true`, new format with opt-out
3. **Phase 3 (Future)**: Remove flag, new format only

### Non-TTY Safety

- Non-TTY detection via `isatty()` (already implemented)
- Queue state always included in log format (no animation)
- No breaking changes to non-TTY output structure

## API Specification for Queue-State Helper

### Module Location
```
tf/ralph/queue_state.py
```

### Data Structure
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class QueueStateSnapshot:
    """Immutable snapshot of queue state at a point in time."""
    ready: int      # Runnable but not running
    blocked: int    # Blocked by unmet deps (MVP: deps-only)
    running: int    # Currently being processed
    done: int       # Completed in current run
    total: int      # Sum of all states

    def __str__(self) -> str:
        """Format: R:3 B:2 (done 1/6)"""
        return f"R:{self.ready} B:{self.blocked} (done {self.done}/{self.total})"
```

### Function Signature
```python
def get_queue_state(
    pending: set[str],      # Tickets waiting to run
    running: set[str],      # Tickets currently running
    completed: set[str],    # Tickets completed (success/fail)
    dep_graph: dict[str, set[str]]  # Ticket -> unmet deps mapping
) -> QueueStateSnapshot:
    """
    Compute queue state snapshot from scheduler in-memory state.

    Args:
        pending: Set of ticket IDs in the pending queue
        running: Set of ticket IDs currently being processed
        completed: Set of ticket IDs completed in current run
        dep_graph: Mapping of ticket ID -> set of unmet dependency IDs

    Returns:
        QueueStateSnapshot with computed counts

    Complexity: O(|pending| + |running| + |completed|)
    """
```

## Integration Points

### RalphLogger Integration

Add method to include queue state in log context:

```python
def log_ticket_start(self, ticket: str, queue_state: QueueStateSnapshot, ...):
    if self.is_tty:
        # Progress display handles formatting
        pass
    else:
        self.info(f"Starting ticket {ticket} [{queue_state}]")
```

### ProgressDisplay Integration

Update to accept queue state:

```python
def start_ticket(self, ticket_id: str, iteration: int, queue_state: QueueStateSnapshot):
    self.queue_state = queue_state
    self._draw(f"[{iteration + 1}/{queue_state.total}] Processing {ticket_id}...  {queue_state}")
```

## Acceptance Criteria Verification

| Criterion | Status | Notes |
|-----------|--------|-------|
| Semantics explicitly defined | ✅ | Ready/blocked/running/done defined above |
| Ready excludes running | ✅ | Invariant #1 documented |
| Blocked is deps-only for MVP | ✅ | Constraint documented |
| TTY output format specified | ✅ | `R:3 B:2 (done 1/6)` format |
| Non-TTY output format specified | ✅ | Log line format with no control chars |
| Backwards-compat strategy chosen | ✅ | Flag-gated approach recommended |

## Files Changed

- Created: `.tf/knowledge/tickets/pt-m54d/research.md`
- Created: `.tf/knowledge/tickets/pt-m54d/implementation.md`

## Verification

This specification enables:
1. pt-oa8n: Implementation of queue-state helper
2. pt-ussr: Update progress display with counts
3. pt-ri6k: Test cases for queue-state invariants

## Downstream Dependencies

| Ticket | Depends On | Description |
|--------|------------|-------------|
| pt-oa8n | pt-m54d | Implement queue-state snapshot helper |
| pt-ussr | pt-oa8n | Update Ralph progress display |
| pt-ri6k | pt-oa8n | Add tests for queue-state counts |
