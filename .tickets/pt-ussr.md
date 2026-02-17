---
id: pt-ussr
status: closed
deps: [pt-oa8n]
links: [pt-ri6k, pt-g6be]
created: 2026-02-10T12:06:01Z
type: task
priority: 2
assignee: legout
external-ref: seed-show-ready-and-blocked-ticket-count
tags: [tf, backlog, component:cli, component:workflow]
---
# Update Ralph progress display to show ready/blocked counts

## Task
Update the Ralph progress indicator to show ready/blocked counts (and done/total if available) instead of only `[x/y]`.

## Context
Plan requires R/B counts derived from in-memory scheduler state, TTY-safe output (no control chars in non-TTY), and backwards-compatible formatting (prefer gating changes behind a flag).
Progress should help operators quickly see whether the queue is blocked on dependencies.

## Acceptance Criteria
- [ ] In TTY, progress display includes `R:<n> B:<n>` and `done x/y` (or equivalent)
- [ ] In non-TTY, output remains readable (no animated control characters)
- [ ] Counts update when deps resolve (blocked → ready)

## Constraints
- Avoid expensive recomputation (no repeated full ticket re-listing).
- Do not break existing output contracts; prefer additive output or gated formatting.
- Non-TTY output must be readable (no animated control characters).
- Blocked is deps-only for MVP; exclude running ticket from ready.

## References
- Seed: seed-show-ready-and-blocked-ticket-count
- Plan: plan-ready-blocked-counts-ralph


## Notes

**2026-02-10T12:49:13Z**

Implementation verified: Ralph progress display shows ready/blocked counts (R:<n> B:<n>) and done/total. All 74 tests pass. No Critical/Major issues found in review.

**2026-02-10T12:51:01Z**

Implementation complete. Ralph progress display now shows ready/blocked counts (R:<n> B:<n>) and done/total in both TTY and non-TTY modes. All 74 tests pass. Commit: 7bed29f
