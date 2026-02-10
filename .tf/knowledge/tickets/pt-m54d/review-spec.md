# Review (Spec Audit): pt-m54d

## Overall Assessment
The current codebase still prints the legacy `[iteration/total]` progress line and generic log messages; the freshly written spec/plan for ready/blocked queue semantics has not been implemented, so none of the acceptance criteria are satisfied.

## Critical (must fix)
- `tf/ralph.py:22-90` – `ProgressDisplay.start_ticket/complete_ticket` still only show `[iteration/total]` with no mention of `ready`, `blocked`, `done` or `total` counts, both in TTY and non-TTY mode. The spec explicitly requires `R:{ready} B:{blocked} (done {done}/{total})` appended to every progress message (the same format described for TTY in-place updates and non-TTY log lines), so the new progress contract is never delivered.
- `tf/logger.py:269-300` – `RalphLogger.log_ticket_start` and `log_ticket_complete` log only ticket id/iteration/status. The plan mandates that normal logging also includes the current queue state (ready/blocked counts plus done/total) for every ticket start and finish; without this metadata, the reviewed output contract is still unchanged.

## Major (should fix)
- `tf/ralph.py:274-284` & `tf/ralph.py:1470-1510` – There is no `QueueStateSnapshot` or queue-state helper, no dependency graph tracking, and the only queue accounting is a one-time `tk ready` call to seed a ready count. The spec requires deriving ready/blocked/running/done totals from in-memory scheduler state (`pending`, `running`, `completed`, `dep_graph`) so counts update with state transitions without expensive recomputation; the existing implementation never tracks blocked tickets or running/done totals, so the semantics defined in the plan cannot be produced at any point.

## Minor (nice to fix)
- `tf/ralph.py:94-117` – The new config/feature flag proposed in the spec (`showQueueState` or similar) does not exist in `DEFAULTS`, and there is no gating logic around the new output contract. Without the flag (and its default/backwards-compatible plan), any future change to the progress/log format would be a breaking change for scripts that consume Ralph output, contravening the backward-compatibility requirement.

## Warnings (follow-up ticket)
- None.

## Suggestions (follow-up ticket)
- None.

## Positive Notes
- `tf/ralph.py:66-80` already prefixes progress updates with the required HH:MM:SS timestamp, so the new queue-state string can be appended to an existing timestamped line.

## Summary Statistics
- Critical: 2
- Major: 1
- Minor: 1
- Warnings: 0
- Suggestions: 0

## Spec Coverage
- Spec/plan sources consulted: `.tf/knowledge/topics/plan-ready-blocked-counts-ralph/plan.md`, `.tf/knowledge/tickets/pt-m54d/implementation.md`, `.tf/knowledge/topics/seed-show-ready-and-blocked-ticket-count/seed.md`
- Missing specs: none
