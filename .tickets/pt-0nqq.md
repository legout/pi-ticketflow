---
id: pt-0nqq
status: closed
deps: [pt-ynqf]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:cli, component:workflow]
---
# CLN-08: Converge asset install/update flow onto one planner implementation

## Task
Reduce duplicated manifest/install/update logic and standardize on one asset flow.

## Context
init/sync/update paths currently overlap in responsibilities.

## Acceptance Criteria
- [ ] One canonical planner for asset routing/install decisions
- [ ] init/sync/update commands continue to work
- [ ] Tests updated for converged behavior

## Constraints
- Keep user-facing command contract stable

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T15:49:12Z**

## Implementation Complete

Converged asset install/update flow onto one canonical planner implementation.

### Changes
- Created  - canonical planner for all asset routing/install decisions
- Refactored  to use asset_planner
- Refactored  to use asset_planner
- Updated  to use asset_planner
- Added comprehensive tests in 

### Review Issues Fixed
- Added network timeout (30s) to prevent indefinite hangs
- Fixed exception chaining to preserve tracebacks
- Replaced SystemExit with RuntimeError for programmatic use
- Extracted duplicate chmod code into helper function
- Fixed duplicate imports

### Verification
- All 541 tests pass
- Commit: bfafb36

### Artifacts
- 
- 
- 
