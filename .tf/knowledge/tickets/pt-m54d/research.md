# Research: pt-m54d - Ralph Ready/Blocked Semantics + Output Contract

## Status
Research complete. This ticket defines specifications for the queue-state feature (pt-oa8n and pt-ussr depend on it).

## Sources Reviewed

### Primary Sources
1. **Ralph Implementation** (`tf/ralph.py`)
   - Current progress display uses `[iteration/total]` format
   - `ProgressDisplay` class handles TTY vs non-TTY output
   - `list_ready_tickets()` function queries ready tickets via `tk ready`
   - Parallel mode uses component tag-based selection
   - Serial mode has progress indicator support

2. **Plan Document** (`.tf/knowledge/topics/plan-ready-blocked-counts-ralph/plan.md`)
   - Defines requirements for ready/blocked counts
   - Specifies display format: `R:3 B:2 (done 1/6)`
   - Identifies state definitions and constraints

3. **Seed Document** (`.tf/knowledge/topics/seed-show-ready-and-blocked-ticket-count/seed.md`)
   - Vision: operators should understand why progress is slow
   - Key features: progress bar counts + normal logging counts

4. **Linked Tickets**
   - **pt-oa8n**: Implement queue-state snapshot helper (depends on this ticket)
   - **pt-ussr**: Update Ralph progress display to show ready/blocked counts (depends on pt-oa8n)
   - **pt-ri6k**: Add tests for queue-state counts

## Current State Analysis

### Existing Progress Display
```python
class ProgressDisplay:
    def start_ticket(self, ticket_id: str, iteration: int, total_tickets: Union[int, str])
    def complete_ticket(self, ticket_id: str, status: str, iteration: int)
```
- Uses `[iteration/total]` format
- TTY mode: `\x1b[2K\r` for in-place updates
- Non-TTY mode: plain text, no control characters
- Timestamp prefix: `HH:MM:SS`

### Current Ticket Selection
- Serial: `select_ticket()` picks first ready ticket
- Parallel: `select_parallel_tickets()` picks by component diversity
- Queue state is not tracked in-memory; recomputed via `tk ready` calls

## Key Findings

### State Semantics Requirements
From plan document and seed:
- **Ready**: tickets that are runnable but not currently running
- **Blocked**: tickets that cannot run due to unmet dependencies (deps-only for MVP)
- **Running**: ticket(s) currently being processed
- **Done**: tickets completed (success or failure)

### Output Format Requirements
- Progress bar: `R:3 B:2 (done 1/6)` format
- Must work in TTY (animated) and non-TTY (plain text) modes
- Normal logging should include counts at ticket start/finish

### Backwards Compatibility
- Current output format `[iteration/total]` may be used by scripts
- Need flag-gated or additive approach for format changes
- Non-TTY output must remain readable

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Definition of "blocked" | Deps-only for MVP; other reasons (filters, locks, failures) out of scope |
| Running ticket in ready? | No - running ticket is excluded from ready count |
| Best display format | `R:3 B:2 (done 1/6)` - human-readable and machine-parseable |
| Count computation source | In-memory scheduler state (no external `tk` calls) |

## Implementation Notes for Downstream Tickets

### For pt-oa8n (Queue-state helper)
- Create `tf/ralph/queue_state.py` module
- Function signature: `get_queue_state() -> QueueStateSnapshot`
- Returns: ready_count, blocked_count, running_count, done_count, total_count
- Must be O(n) over in-memory ticket list

### For pt-ussr (Progress display update)
- Update `ProgressDisplay` class to accept queue state
- Add new format option (gated by config flag)
- Integrate with `RalphLogger` for normal logging counts

## References
- Plan: `.tf/knowledge/topics/plan-ready-blocked-counts-ralph/plan.md`
- Seed: `.tf/knowledge/topics/seed-show-ready-and-blocked-ticket-count/seed.md`
