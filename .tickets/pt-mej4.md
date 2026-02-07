---
id: pt-mej4
status: closed
deps: [pt-np39, pt-pa5v]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:tests]
---
# CLN-14: Raise coverage gate incrementally and add tests for low-covered user-facing modules

## Task
Increase coverage floor in stages and add tests for low-covered user-facing modules.

## Context
Coverage gate is currently too low to prevent regressions in setup/ops commands.

## Acceptance Criteria
- [ ] Coverage threshold roadmap agreed and applied incrementally
- [ ] New tests added for setup/login/tags/seed/agentsmd (and other low-coverage modules)
- [ ] CI reflects updated quality bar

## Constraints
- Avoid abrupt threshold jumps that block all progress

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T16:50:41Z**

Implementation complete. Raised coverage gate from 25% to 35% and added 114 tests across 5 previously uncovered modules (setup, login, tags_suggest, seed_cli, agentsmd). Coverage improved from 49.5% to 59.4%. All 693 tests pass. Commit: be30b90
