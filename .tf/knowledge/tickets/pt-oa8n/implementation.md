# Implementation: pt-oa8n - Queue-State Snapshot Helper

## Summary
Implemented a queue-state snapshot helper that computes ready/blocked/running/done counts from Ralph's in-memory scheduler state, following the pt-m54d specification.

## Files Changed

### Created: `tf/ralph/__init__.py`
- Ralph subpackage initialization
- Exports `QueueStateSnapshot` and `get_queue_state`

### Created: `tf/ralph/queue_state.py`
- `QueueStateSnapshot` dataclass with frozen semantics
- `get_queue_state()` function for computing queue state
- `get_queue_state_from_scheduler()` convenience wrapper

## Implementation Details

### QueueStateSnapshot
- Immutable dataclass (frozen=True)
- Validates invariant: total = ready + blocked + running + done
- `__str__()` returns format: `R:3 B:2 (done 1/6)`
- `to_log_format()` returns format: `R:3 B:2 done:1/6`

### get_queue_state()
- Computes counts from pending/running/completed sets and dep_graph
- Validates that state sets are disjoint
- Blocked count: pending tickets with entries in dep_graph
- Ready count: pending tickets minus blocked tickets
- Complexity: O(|pending| + |running| + |completed|)

### Semantics Compliance
| Requirement | Implementation |
|-------------|----------------|
| Ready excludes running | ✅ Yes - running is separate count |
| Blocked is deps-only | ✅ Yes - checks dep_graph entries |
| No external tk calls | ✅ Yes - pure in-memory computation |
| Frozen/immutable snapshot | ✅ Yes - dataclass(frozen=True) |

## API Usage

```python
from tf.ralph.queue_state import QueueStateSnapshot, get_queue_state

pending = {"T-1", "T-2", "T-3"}
running = {"T-4"}
completed = {"T-5"}
dep_graph = {"T-2": {"T-1"}}  # T-2 blocked on T-1

snapshot = get_queue_state(pending, running, completed, dep_graph)
print(snapshot)  # R:2 B:1 (done 1/5)
```

## Acceptance Criteria Verification

- [x] Helper returns counts: ready, blocked, running, done, total
- [x] Blocked is deps-only for MVP
- [x] Running is excluded from ready
- [x] No external `tk` calls required

## Tests Run

```bash
# Type checking
pyright tf/ralph/queue_state.py

# Import check
python -c "from tf.ralph.queue_state import QueueStateSnapshot, get_queue_state; print('OK')"
```

## Downstream Impact

This implementation unblocks:
- pt-ussr: Update Ralph progress display to show ready/blocked counts
- pt-ri6k: Add tests for queue-state counts + progress/log formatting
