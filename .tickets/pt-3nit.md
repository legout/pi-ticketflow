---
id: pt-3nit
status: closed
deps: [pt-paih]
links: []
created: 2026-02-06T13:07:53Z
type: task
priority: 2
assignee: legout
external-ref: plan-kb-management-cli
tags: [tf, backlog, plan, knowledge]
---
# Implement tf kb validate

## Task
Implement `tf kb validate` to detect index drift.

## Acceptance Criteria
- [ ] Detect missing files referenced by index entries.
- [ ] Detect orphan dirs under `.tf/knowledge/topics/*` that are not in index.
- [ ] Detect duplicate topic IDs.
- [ ] Exit code non-zero when errors are found.

## References
- Plan: plan-kb-management-cli



## Notes

**2026-02-06T13:35:27Z**

Implemented tf kb validate command.

Features:
- Detects missing files referenced by index entries (overview, sources, plan, backlog)
- Detects orphan directories under topics/* not in index
- Detects duplicate topic IDs
- Non-zero exit code when errors found
- Supports --json output format
- Includes --knowledge-dir override support

Commit: bd71e66
Tests: All 281 tests pass
