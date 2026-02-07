---
id: pt-np39
status: closed
deps: [pt-g42s]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 2
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:cli]
---
# CLN-11: Rename *_new.py modules to stable names and update all references

## Task
Rename transitional *_new.py modules and update imports/tests/docs.

## Context
The *_new suffix is migration residue and adds cognitive overhead.

## Acceptance Criteria
- [ ] Module names normalized
- [ ] Imports and CLI dispatch updated
- [ ] Tests and docs references updated

## Constraints
- Keep runtime behavior unchanged

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T16:37:44Z**

--note ## Implementation Complete

### Summary
Renamed all transitional *_new.py modules to stable names and updated all references.

### Changes
- 13 source modules renamed in tf_cli/
- 5 test files renamed in tests/
- Updated imports in cli.py, new_cli.py, setup.py
- Fixed test imports and patch references

### Test Results
All 579 tests pass.

### Commit
41133ff pt-np39: Rename *_new.py modules to stable names

### Review
- Critical issues found: 8 (all fixed)
- Major issues: 1
- Minor issues: 1

### Artifacts
- .tf/knowledge/tickets/pt-np39/implementation.md
- .tf/knowledge/tickets/pt-np39/review.md
- .tf/knowledge/tickets/pt-np39/fixes.md
