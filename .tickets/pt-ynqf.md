---
id: pt-ynqf
status: closed
deps: [pt-7sv0]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:cli]
---
# CLN-06: Refactor CLI modules to consume shared utilities (no behavior-change pass)

## Task
Refactor affected CLI modules to import shared utilities instead of local duplicates.

## Context
Utility extraction is only useful if duplicated definitions are removed from callers.

## Acceptance Criteria
- [ ] Target modules import shared helpers
- [ ] Duplicate helper definitions removed
- [ ] Full test suite passes unchanged behavior

## Constraints
- No command semantics changes in this pass

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T15:35:20Z**

Refactored ralph_new.py and ticket_factory.py to import find_project_root from tf_cli.utils. Removed 18 lines of duplicate code. All 512 tests pass. Commit: 59619a4
