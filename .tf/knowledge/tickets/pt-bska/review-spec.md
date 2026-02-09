# Review (Spec Audit): pt-bska

## Overall Assessment
The implementation satisfies all acceptance criteria for the ticket: ProgressDisplay.start_ticket() now accepts `total_tickets` separate from `max_iterations`, the UI total is derived from `list_ready_tickets()`, and `max_iterations` remains a pure loop limit with logging intact. However, the implementation computes `total_tickets` per-iteration inside the loop rather than once at loop start, which violates the plan's "at start" requirement and lightweight constraint.

## Critical (must fix)
None - all acceptance criteria are met.

## Major (should fix)
- `tf_cli/ralph.py:1532-1534` - `total_tickets` is computed inside the loop for each ticket processing iteration via `list_ready_tickets(ticket_list_query(ticket_query))`. The plan requirement explicitly states "compute the progress total from the current backlog: total = len(list_ready_tickets(ticket_list_query(ticket_query))) at start" and the blocking ticket pt-qu8a AC1 states "derived from `len(list_ready_tickets(...))` computed once at loop start." Computing this per iteration violates both the plan's "at start" specification and the constraint "Must stay lightweight (no expensive per-iteration work)." This could cause performance degradation, especially for larger backlogs.

## Minor (nice to fix)
None

## Warnings (follow-up ticket)
None

## Suggestions (follow-up ticket)
- `tf_cli/ralph.py:1532-1534` - Consider moving the `list_ready_tickets()` call outside the loop (before line 1513) to compute `total_tickets` once at loop start. This would align with the plan's design intent and improve performance by avoiding repeated subprocess calls to `tk ready`. The value could be stored in a variable and reused in each `start_ticket()` call.

## Positive Notes
- `tf_cli/ralph.py:39-48` - ProgressDisplay.start_ticket() signature correctly changed from `total` to `total_tickets` parameter with comprehensive docstring explaining the purpose
- `tf_cli/ralph.py:1534` - UI total properly decoupled from `max_iterations`; `total_tickets` is derived from ready tickets via `len(list_ready_tickets(...))`
- `tf_cli/ralph.py:1493` - Existing logging that reports `max_iterations` remains intact via `logger.log_loop_start(..., max_iterations=max_iterations, ...)`
- `tf_cli/ralph.py:1513` - `max_iterations` remains purely a loop limit in `while iteration < max_iterations`, not passed to progress display
- Tests pass (22 passed for test_progress_display.py, 11 passed for test_ralph_state.py)
- Implementation correctly handles both TTY and non-TTY modes for progress display
- Changes are localized to the progress display area as required by constraints

## Summary Statistics
- Critical: 0
- Major: 1
- Minor: 0
- Warnings: 0
- Suggestions: 1

## Spec Coverage
- Spec/plan sources consulted:
  - Ticket pt-bska: Refactor progress display API to accept total_tickets separate from max_iterations
  - Plan: plan-fix-ralph-progressbar-counter
  - Blocking ticket pt-qu8a: Compute correct progress total for tf ralph --progress (ready tickets snapshot)
  - Seed: seed-fix-progressbar-counter-currently-it-sho
- Missing specs: none
