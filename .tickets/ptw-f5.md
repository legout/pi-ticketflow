---
id: ptw-f5
status: closed
deps: []
links: []
created: 2026-02-05T15:25:00Z
type: task
priority: 3
assignee: legout
external-ref: ptw-6dza
tags: [tf, followup]
---
# Document out-of-order ticket creation behavior

## Origin
From review of ticket: ptw-6dza
File: prompts/tf-backlog.md and skills/tf-planning/SKILL.md

## Issue
The default chain logic assumes sequential creation order, which may not hold in practice. Consider adding a note about what happens when tickets are created out of order (e.g., user adds ticket 5 before ticket 3).

## Severity
Suggestion

## Acceptance Criteria
- [ ] Document behavior when tickets are created out of order
- [ ] Explain how the default chain handles non-sequential creation
- [ ] Consider adding guidance for manual dependency adjustment in such cases

## Notes

**2026-02-05T16:57:17Z**

## Completed: Document out-of-order ticket creation behavior

### Changes Made
- Updated  with out-of-order creation explanation and manual correction guidance
- Updated  with matching documentation

### Key Documentation Added
The default dependency chain is based on **creation sequence**, not ticket IDs. If ticket 5 is created before ticket 3:
- Ticket 5 has no dependency (first created)
- Ticket 3 depends on ticket 5 (previous in creation order)

### Manual Correction
To fix out-of-order dependencies:


### Commit

