---
id: pt-qqwc
status: closed
deps: [pt-gn5z]
links: [pt-1fsy]
created: 2026-02-06T13:51:23Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:cli, component:workflow]
---
# Implement ticket selection for priority reclassify (ids/ready/status/tag)

## Task
Implement selecting tickets to reclassify: explicit IDs, `--ready`, and basic filters like `--status` and `--tag`.

## Context
The command should support bulk triage (e.g. reclassify all “ready” tickets) without touching closed tickets by default.

## Acceptance Criteria
- [ ] Supports explicit ticket IDs (partial IDs allowed via `tk show`).
- [ ] Supports `--ready` (uses `tk ready`).
- [ ] Excludes closed tickets by default; can include with an explicit flag.

## Constraints
- Must be read-only when `--apply` is not set.

## References
- Seed: seed-pi-command-reclassify-priorities


## Notes

**2026-02-06T14:08:54Z**

## Implementation Complete

Implemented ticket selection for priority reclassify command:

**Changes:**
- Added --include-closed flag to tf_cli/priority_reclassify_new.py
- Created comprehensive test suite (tests/test_priority_reclassify.py) with 26 tests

**Features:**
- ✅ Explicit ticket IDs via --ids (supports partial IDs via tk show)
- ✅ --ready flag to process all ready tickets
- ✅ --status filter for filtering by status
- ✅ --tag filter for filtering by tag
- ✅ Closed tickets excluded by default, included with --include-closed
- ✅ Read-only mode by default (dry-run), changes applied with --apply

**Verification:**
- All 26 new tests pass
- All 372 existing tests pass

Commit: a501426
