---
id: pt-gmpy
status: closed
deps: [pt-m2qh]
links: [pt-m2qh, pt-4sw6]
created: 2026-02-07T14:23:31Z
type: task
priority: 2
assignee: legout
external-ref: seed-when-executing-tf-backlog-in-an-active-s
tags: [tf, backlog, component:config, component:docs, component:workflow]
---
# Implement /tf-backlog: include session plan/spike docs as backlog inputs

## Task
When a session is active, incorporate the session’s linked plan and spikes as inputs for backlog ticket generation (additional requirements/constraints/context).

## Context
Session metadata includes plan id and a list of spike ids. Their docs live under .tf/knowledge/topics/<id>/. Using them as inputs should reduce missed requirements when generating tickets.

## Acceptance Criteria
- [ ] If session.plan is set, /tf-backlog reads the plan doc and incorporates requirements/constraints into ticket descriptions (briefly; no long pastes)
- [ ] If session.spikes[] is non-empty, /tf-backlog reads spike docs and incorporates relevant findings into ticket context
- [ ] Output prints a short “inputs used” summary (seed + plan present + spike count)

## Constraints
- Keep created tickets self-contained (no requirement to open multiple docs to implement)
- Conservative: if a doc is missing/unreadable, continue with seed-only (but warn)

## References
- Seed: seed-when-executing-tf-backlog-in-an-active-s



## Notes

**2026-02-07T16:28:48Z**

Implemented session plan/spike input incorporation for /tf-backlog

Changes:
- Added Phase B: Session Input Incorporation (reads plan.md and spike.md docs)
- Added 'Inputs Used Summary' output format
- Added 'Seed with Session Inputs' template
- Enhanced session finalization with inputs_used tracking
- Fixed JSON examples to include inputs_used field

Commit: 3fbe3cc
