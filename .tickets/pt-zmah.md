---
id: pt-zmah
status: closed
deps: [pt-4eor]
links: [pt-4eor]
created: 2026-02-13T16:05:22Z
closed: 2026-02-14T10:51:00Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-ralph-loop-background-interactive
tags: [tf, backlog, component:cli, component:workflow]
---
# Add dispatch session observability and attach hints

## Task
Improve observability by logging session IDs, attach instructions, and output artifact pointers.

## Context
Users want optional live monitoring without mandatory interaction.
Operators need quick links to session/output data when diagnosing failures.

## Acceptance Criteria
- [x] Ralph logs session ID for each dispatched ticket.
- [x] Logs include how to attach/watch a running session.
- [x] Output capture paths are recorded for completed/failed tickets.

## Implementation
Modified `tf/ralph.py::run_ticket_dispatch()` and `ralph_start()` to add:

1. **Session ID logging**: Each dispatch now logs its session ID immediately after launch
2. **Attach instructions**: Users see `To attach and watch: pi /attach <session_id>` 
3. **List background hint**: Users see `To watch: pi /list-background | grep <ticket>`
4. **Output capture paths**: 
   - File mode: logs `Output will be captured at: <path>`
   - JSON mode: logs `JSON output will be captured at: <path>`
5. **Completion artifacts**: On ticket completion/failure, logs both log and JSON paths with session_id

All changes maintain concise default logs while providing actionable observability for operators.

## Constraints
- Keep default logs concise; avoid noisy output explosion.

## References
- Seed: seed-add-ralph-loop-background-interactive
- Plan: plan-ralph-background-interactive-shell
- Spike: spike-interactive-shell-execution

