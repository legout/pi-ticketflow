---
id: pt-m54d
status: closed
deps: []
links: [pt-oa8n]
created: 2026-02-10T12:06:01Z
type: task
priority: 2
assignee: legout
external-ref: seed-show-ready-and-blocked-ticket-count
tags: [tf, backlog, component:cli, component:docs, component:workflow]
---
# Define Ralph ready/blocked semantics + output contract

## Task
Define the queue-state semantics (ready/blocked/running/done) and the exact output formats for progress + normal logs.

## Context
Operators need to see whether progress is slow due to many blocked tickets vs few ready tickets; counts should update as dependencies resolve.
Plan requires R/B counts derived from in-memory scheduler state, TTY-safe output (no control chars in non-TTY), and backwards-compatible formatting (prefer gating changes behind a flag).

## Acceptance Criteria
- [ ] Semantics are explicitly defined: ready excludes running; blocked is deps-only for MVP
- [ ] Output format is specified for TTY and non-TTY (e.g. `R:3 B:2 (done 1/6)`)
- [ ] Backwards-compat strategy is chosen (flag-gated vs always-on) and documented

## Constraints
- Avoid expensive recomputation (no repeated full ticket re-listing).
- Do not break existing output contracts; prefer additive output or gated formatting.
- Non-TTY output must be readable (no animated control characters).
- Blocked is deps-only for MVP; exclude running ticket from ready.

## References
- Seed: seed-show-ready-and-blocked-ticket-count
- Plan: plan-ready-blocked-counts-ralph


## Notes

**2026-02-10T12:25:47Z**

Completed: Defined Ralph queue-state semantics and output contract.

## Summary
- Defined queue states: ready, blocked, running, done
- Specified output format: R:{ready} B:{blocked} (done {done}/{total})
- Documented TTY and non-TTY output formats
- Recommended flag-gated backwards compatibility strategy
- Specified QueueStateSnapshot API for pt-oa8n implementation

## Artifacts
- research.md: Analysis of current Ralph implementation and requirements
- implementation.md: Complete specification document
- review.md: 3-reviewer consensus (0 critical/major/minor issues)

## Downstream Impact
- Unblocks pt-oa8n (queue-state helper implementation)
- Unblocks pt-ussr (progress display update)
- Unblocks pt-ri6k (queue-state tests)

Commit: 42d04fc
