---
id: pt-qayw
status: closed
deps: []
links: [pt-7i3q, pt-ul76]
created: 2026-02-07T14:17:18Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-ticket-title-in-the-logging-when-run
tags: [tf, backlog, component:tests, component:workflow]
---
# Add ticket_title context field to RalphLogger for verbose logs

## Task
Add ticket_title context field to RalphLogger so verbose logs include the ticket title alongside the ID.

## Context
When running tf ralph --verbose, logs currently only show ticket IDs. Adding the title will make runs easier to understand and debug. The title should be fetched once per ticket and cached to avoid repeated subprocess calls.

## Acceptance Criteria
- [ ] RalphLogger accepts ticket_title in context or via with_context()
- [ ] Verbose logs include ticket_title field when available
- [ ] Graceful fallback when title is unavailable (omitted or "<unknown>")
- [ ] Non-verbose output unchanged

## Constraints
- Keep formatting readable and parseable
- Avoid performance regression

## References
- Seed: seed-add-ticket-title-in-the-logging-when-run


## Notes

**2026-02-07T16:57:35Z**

Implementation complete: Added ticket_title context field to RalphLogger.\n\nChanges:\n- logger.py: Added ticket_title parameter to create_logger() and all ticket-related log methods\n- ralph.py: Added extract_ticket_title() and extract_ticket_titles() helpers, updated all logging calls to include ticket_title\n\nMajor fix during review: Changed extract_ticket_title() to return None on failure (instead of ticket ID) to enable graceful omission.\n\nAll 693 tests pass.\nCommit: 77080f5
