---
id: pt-tl00
status: closed
deps: [pt-9uxj]
links: [pt-9uxj]
created: 2026-02-10T12:39:47Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-retry-logic-on-failed-tickets
tags: [tf, backlog, component:config, component:docs, component:tests, component:workflow]
---
# Ralph integration: cap retries and stop thrashing on blocked tickets

## Task
Ensure Ralph does not repeatedly pick the same quality-gate blocked ticket forever.

## Context
Ralph selects tickets via `tk ready`. If a ticket stays open, it may be retried indefinitely. We need maxRetries enforcement + clear reporting when a ticket is blocked beyond the cap.
This backlog is derived from an approved plan (plan-retry-logic-quality-gate-blocked, status=approved).

## Acceptance Criteria
- [ ] Ralph reads retry state and stops retrying after `workflow.escalation.maxRetries`.
- [ ] Ralph progress/history records retry attempt count and final blocked outcome.
- [ ] Document/guard against `parallelWorkers > 1` without ticket locking.

## Constraints
- Must avoid infinite loops.

## References
- Seed: seed-add-retry-logic-on-failed-tickets
- Plan: plan-retry-logic-quality-gate-blocked


## Notes

**2026-02-10T13:52:09Z**

Fixed retry capping bug in is_ticket_blocked_by_retries(). Changed from checking aggregate status to last attempt status. All 60 tests pass.
