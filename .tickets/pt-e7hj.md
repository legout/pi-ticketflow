---
id: pt-e7hj
status: closed
deps: []
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 0
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:docs, component:config]
---
# CLN-01: Define runtime artifact policy for .tf/.tickets/generated outputs

## Task
Define and document what is source-controlled vs runtime/generated state.

## Context
The repo currently mixes implementation code with local runtime artifacts.
A clear policy is needed before cleanup changes.

## Acceptance Criteria
- [ ] Policy doc created and linked from README/docs
- [ ] Explicit rules for .tf/knowledge, .tf/ralph/sessions, .tickets, htmlcov, *.egg-info
- [ ] Contributor guidance for local-only state

## Constraints
- Keep guidance short and actionable

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T13:48:16Z**

--note-file -
