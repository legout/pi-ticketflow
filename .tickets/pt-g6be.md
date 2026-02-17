---
id: pt-g6be
status: closed
deps: [pt-ussr]
links: [pt-ussr]
created: 2026-02-10T12:06:01Z
type: task
priority: 2
assignee: legout
external-ref: seed-show-ready-and-blocked-ticket-count
tags: [tf, backlog, component:api, component:workflow]
---
# Add ready/blocked counts to normal Ralph logging (ticket start/finish)

## Task
When running Ralph with normal (non-progressbar) logging, include ready/blocked counts on ticket start and ticket finish.

## Context
The user request explicitly asks for ready/blocked counts in normal logging when starting/finishing a ticket.

## Acceptance Criteria
- [ ] On ticket start log line includes current `R:<n> B:<n>` (and done/total if available)
- [ ] On ticket finish log line includes updated counts
- [ ] Errors still print immediately and remain prominent

## Constraints
- Avoid expensive recomputation (no repeated full ticket re-listing).
- Do not break existing output contracts; prefer additive output or gated formatting.
- Non-TTY output must be readable (no animated control characters).
- Blocked is deps-only for MVP; exclude running ticket from ready.

## References
- Seed: seed-show-ready-and-blocked-ticket-count
- Plan: plan-ready-blocked-counts-ralph


## Notes

**2026-02-10T12:56:07Z**

Implementation complete. Added ready/blocked counts (R:<n> B:<n> done:<n>/<n>) to normal Ralph logging on ticket start and finish. Fixed inconsistency in failure path logging. All 121 tests pass. Commit: 70fe231
