# Fixes: pt-bska

## Summary
Addressed major review issues related to UX accuracy when max_iterations limits execution.

## Files Changed
- `tf_cli/ralph.py` - Enhanced progress display logic

## Review Issues Addressed

### Major Issue: Total may exceed tickets actually processed (FIXED)
- **Location**: `tf_cli/ralph.py:1531-1537`
- **Problem**: If `max_iterations=2` but there are 10 ready tickets, progress showed `[1/10]`, `[2/10]` which was confusing
- **Fix**: Use `min(len(ready_tickets), remaining_iterations)` to show accurate expected completion count
- **Result**: Now shows `[1/2]`, `[2/2]` when max_iterations limits execution

### Minor Issue: Edge case total_tickets=0 (FIXED)
- **Location**: `tf_cli/ralph.py:1537`
- **Problem**: If ready list is empty due to race condition, progress would show `[N/0]`
- **Fix**: Added `max(total_tickets, 1)` to ensure at least 1 for display

## Implementation Details

```python
# Get total tickets for accurate progress display (decoupled from max_iterations)
# Use min with remaining iterations to show accurate progress when max_iterations limits execution
ready_tickets = list_ready_tickets(ticket_list_query(ticket_query))
remaining_iterations = max_iterations - iteration
total_tickets = min(len(ready_tickets), remaining_iterations)
# Ensure at least 1 to avoid [N/0] display edge case
total_tickets = max(total_tickets, 1)
progress_display.start_ticket(ticket, iteration, total_tickets)
```

## Re-Testing
```bash
python -m pytest tests/test_progress_display.py tests/test_ralph_state.py -v
# Result: 33 passed (22 progress + 11 state)
```

## Remaining Open Items
The following items were noted in review but intentionally not addressed:

- **Race condition**: Between `select_ticket()` and `list_ready_tickets()` - acceptable risk given typical usage patterns and serial processing
- **Performance**: Shell command on each iteration - acceptable given typical loop delays (5-10s between tickets)
- **Test coverage**: `ticket_list_query()` and `list_ready_tickets()` error handling - existing behavior preserved
