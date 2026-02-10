# Fixes: pt-oa8n

## Summary
Fixed 1 Critical and 1 Major issue identified during code review.

## Fixes Applied

### Critical: Fixed type annotation `Optional[callable]` → `Optional[Callable]`
- **File**: `tf/ralph/queue_state.py`
- **Line**: 160 (now 159)
- **Change**: 
  - Added `Callable` to imports from `typing`
  - Changed `Optional[callable]` to `Optional[Callable[[str], set[str]]]` for proper type annotation

### Major: Removed unused `blocked_tickets` set
- **File**: `tf/ralph/queue_state.py`
- **Lines**: 117-119
- **Change**: Removed the `blocked_tickets: set[str] = set()` variable and `blocked_tickets.add(ticket)` call since the set was never used after being built.

## Verification

```bash
python -c "
from tf.ralph.queue_state import QueueStateSnapshot, get_queue_state, get_queue_state_from_scheduler

# Test basic functionality
pending = {'T-1', 'T-2', 'T-3'}
running = {'T-4'}
completed = {'T-5'}
dep_graph = {'T-2': {'T-1'}}

snapshot = get_queue_state(pending, running, completed, dep_graph)
assert str(snapshot) == 'R:2 B:1 (done 1/5)'

# Test convenience wrapper with Callable
def mock_resolver(ticket):
    return {'T-2': {'T-1'}}.get(ticket, set())

snapshot2 = get_queue_state_from_scheduler(pending, running, completed, mock_resolver)
assert snapshot2 == snapshot

print('All fixes verified!')
"
```

All fixes verified successfully.

## Remaining Issues (Non-blocking)

- **Minor**: Negative count validation not added (low priority - `get_queue_state()` only produces valid counts)
- **Warnings/Suggestions**: Deferred to follow-up tickets as they are enhancements, not defects.
