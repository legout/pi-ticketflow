---
id: pt-7sv0
status: closed
deps: [pt-gzqg]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:cli]
---
# CLN-05: Extract shared CLI utility module for root/config/json helpers

## Task
Create shared utility module and move duplicated CLI helper functions into it.

## Context
find_project_root/read_json/merge-style helpers are duplicated across multiple modules.

## Acceptance Criteria
- [ ] Common module created with tests
- [ ] At least root resolution and JSON helper centralized
- [ ] Existing behavior preserved

## Constraints
- Avoid API churn beyond internals

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T15:31:35Z**

--note-file -
