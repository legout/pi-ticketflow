---
id: pt-ljos
status: closed
deps: [pt-rvpi]
links: [pt-rvpi, pt-2sea]
created: 2026-02-06T17:00:29Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-more-logging-to-ralph-loop
tags: [tf, backlog, component:cli, component:config, component:workflow]
---
# Implement lifecycle logging for serial Ralph loop (start/run)

## Task
Instrument the serial Ralph loop with lifecycle logs: loop start/end, iteration markers, ticket selection outcomes, and per-ticket result summary.

## Context
In serial mode, Ralph repeatedly selects a ready ticket and runs `pi -p "/tf <ticket> ..."`. Logs should make progress visible and failures actionable.

## Acceptance Criteria
- [ ] Logs at least: loop start, selected ticket, running command (sanitized), exit code, and loop completion reason.
- [ ] When no ticket is selected, logs why/how long it will sleep before retry.
- [ ] On failure, log a single error summary that includes ticket id + pointers to `.tf/knowledge/tickets/<id>/`.

## Constraints
- Keep normal mode concise; verbose mode can include more detail.

## References
- Seed: seed-add-more-logging-to-ralph-loop


## Notes

**2026-02-06T18:03:40Z**

Implemented lifecycle logging for serial Ralph loop

Changes:
- Added log_loop_start(), log_loop_complete(), log_no_ticket_selected(), log_command_executed() to RalphLogger
- Updated ralph_start() to use new logging methods with structured context
- Added command sanitization to redact secrets from logged commands
- Fixed security issue where raw commands appeared in structured log fields
- Added iteration support to log_error_summary() and log_no_ticket_selected()

Commit: 7f74340
Artifacts: .tf/knowledge/tickets/pt-ljos/
