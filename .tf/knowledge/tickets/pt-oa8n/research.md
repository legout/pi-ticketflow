# Research: pt-oa8n - Queue-State Snapshot Helper

## Context
This ticket implements the queue-state snapshot helper specified in pt-m54d. The helper computes ready/blocked/running/done counts from Ralph's in-memory scheduler state.

## Specification Reference
From pt-m54d implementation.md:

### State Semantics
- **Ready**: Tickets runnable but not currently being processed
- **Blocked**: Tickets blocked by unmet dependencies (deps-only for MVP)
- **Running**: Tickets currently being processed
- **Done**: Tickets completed during current run
- **Total**: Sum of ready + blocked + running + done

### Key Invariants
1. Running ticket is never counted in ready
2. Blocked is deps-only for MVP
3. Counts derived from in-memory state (no external tk calls)

### API Specification
```python
@dataclass(frozen=True)
class QueueStateSnapshot:
    ready: int
    blocked: int
    running: int
    done: int
    total: int

    def __str__(self) -> str:
        return f"R:{self.ready} B:{self.blocked} (done {self.done}/{self.total})"
```

### Function Signature
```python
def get_queue_state(
    pending: set[str],
    running: set[str],
    completed: set[str],
    dep_graph: dict[str, set[str]]
) -> QueueStateSnapshot
```

## Implementation Notes
- Module location: `tf/ralph/queue_state.py`
- Complexity: O(|pending| + |running| + |completed|)
- Blocked calculation: ticket is blocked if it has unmet deps in dep_graph
- Ready calculation: pending tickets minus blocked tickets

## Sources
- pt-m54d specification: `.tf/knowledge/tickets/pt-m54d/implementation.md`
