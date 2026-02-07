---
id: pt-gzqg
status: closed
deps: [pt-mr22]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 0
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:workflow]
---
# CLN-03: Untrack committed runtime/build artifacts while preserving local data

## Task
Remove runtime/build artifacts from git index without deleting local working data.

## Context
Large runtime/session files are currently tracked and bloat repository history.

## Acceptance Criteria
- [ ] Runtime/build artifact paths removed from git index
- [ ] Local files preserved for current environment
- [ ] Migration note added for collaborators

## Constraints
- Do not rewrite history in this ticket

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T15:22:18Z**

Ticket completed. Untracked 653 runtime/build artifacts from git index while preserving all local files.

Commit: fe40be8
Files removed: 653 (~59,574 lines)
.gitignore updated with patterns for runtime artifacts

Migration note added for collaborators in close-summary.md
