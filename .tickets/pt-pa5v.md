---
id: pt-pa5v
status: closed
deps: [pt-a51k]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:docs]
---
# CLN-12: Reconcile docs and prompts with current CLI/config behavior

## Task
Update docs/prompts to match actual command behavior and config keys.

## Context
Current docs contain drift (legacy command examples, stale config mappings, logging mismatches).

## Acceptance Criteria
- [ ] README/docs/prompts aligned with current CLI behavior
- [ ] Stale command/config references removed
- [ ] Ralph logging docs reflect actual implementation

## Constraints
- Prefer concise docs with clear source-of-truth links

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T16:11:42Z**

Documentation reconciliation complete.

Fixed drift between docs and actual CLI/config behavior:
- Model references updated (review-secop, fast, review-spec)
- Config keys corrected (metaModels, researchParallelAgents=3, failOn=[])
- Ralph logging docs aligned with implementation (uppercase levels, pipe format)
- Added missing Ralph config keys (logLevel, captureJson)

Commit: b23ab0f
