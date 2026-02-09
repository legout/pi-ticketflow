# Implementation: pt-bska

## Summary
Refactored progress display API to accept `total_tickets` separate from `max_iterations`, decoupling the UI display total from the loop limit.

## Files Changed
- `tf_cli/ralph.py` - Modified `ProgressDisplay.start_ticket()` method and its caller in `ralph_start()`

## Key Changes

### 1. ProgressDisplay.start_ticket() signature change
- Renamed parameter `total` → `total_tickets` for clarity
- Added comprehensive docstring explaining the parameters
- The method now explicitly documents that `total_tickets` is for UI display purposes

### 2. Caller update in ralph_start()
- Before: `progress_display.start_ticket(ticket, iteration, max_iterations)`
- After: Computes `total_tickets` from `list_ready_tickets()` and caps it by remaining iterations
- This decouples the displayed progress total from the loop iteration limit
- Uses `min(len(ready_tickets), remaining_iterations)` for accurate UX when max_iterations limits execution
- Guards against zero with `max(total_tickets, 1)` to avoid [N/0] display edge case

## Acceptance Criteria Verification

- [x] `tf_cli/ralph.py` passes a ticket-derived `total` to `ProgressDisplay.start_ticket()`
  - The `total_tickets` value is derived from `len(list_ready_tickets(...))`
  
- [x] `max_iterations` remains purely a loop limit (not UI total)
  - `max_iterations` is only used in `while iteration < max_iterations`
  - It is no longer passed to the progress display
  
- [x] Any existing logging that reports max_iterations remains intact
  - `logger.log_loop_start()` still logs `max_iterations`
  - All other logging remains unchanged

## Tests Run
```bash
python -m pytest tests/test_progress_display.py -v
# Result: 22 passed

python -m pytest tests/test_ralph_state.py -v
# Result: 11 passed
```

## Verification
The progress display will now show the actual number of ready tickets as the total,
rather than the max_iterations value. For example:
- Before: `[1/50] Processing ticket-123...` (when max_iterations=50 but only 3 tickets ready)
- After: `[1/3] Processing ticket-123...` (showing actual ticket count)

This provides more accurate UX while keeping max_iterations as a safety limit for the loop.
