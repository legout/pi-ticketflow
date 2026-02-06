---
id: pt-zoqp
status: closed
deps: []
links: []
created: 2026-02-06T13:51:22Z
closed: 2026-02-06T14:02:00Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:cli, component:docs, component:workflow]
---
# Define priority rubric mapping (P0-P4 → tk priority 0-4)

## Task
Define the canonical mapping from the P0-P4 rubric to Ticketflow/tk numeric priorities (0-4) and document edge cases.

## Context
We want a repeatable rubric for backlog triage so a reclassify command can apply consistent priorities.

## Acceptance Criteria
- [x] Mapping P0–P4 → 0–4 is explicitly stated (including P0 vs P1 semantics).
- [x] "Ambiguous/unknown" handling is defined (e.g., skip + explain).
- [x] 5–10 example scenarios are listed (security, correctness, OOM, feature, refactor/docs).

## Notes
- **Completed**: 2026-02-06
- **Commit**: 5b1c421a4063e645125fbd1a7cbae29ab33517ca
- **Artifact**: `.tf/knowledge/topics/priority-rubric.md`
- **Review**: 0 Critical, 0 Major, 2 Minor, 2 Warnings, 5 Suggestions
- **Unblocks**: pt-gn5z (Design + setup /tf-priority-reclassify)

## Constraints
- Keep MVP rubric simple and deterministic (keyword/tag based).

## References
- Seed: seed-pi-command-reclassify-priorities

