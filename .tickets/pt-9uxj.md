---
id: pt-9uxj
status: closed
deps: [pt-lbvu]
links: [pt-lbvu, pt-tl00]
created: 2026-02-10T12:39:47Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-retry-logic-on-failed-tickets
tags: [tf, backlog, component:agents, component:config, component:tests, component:workflow]
---
# Make quality gate meaningful: post-fix re-review before close

## Task
Add a post-fix verification step so the quality gate checks the state *after* fixes, not the initial review.

## Context
Currently the quality gate can block based on review counts that were produced before the fixer ran. This prevents convergence even when issues are fixed. A lightweight post-fix re-review/re-count is needed.
This backlog is derived from an approved plan (plan-retry-logic-quality-gate-blocked, status=approved).

## Acceptance Criteria
- [ ] When `enableQualityGate` is true, /tf performs post-fix verification (re-review or re-count) before attempting `tk close`.
- [ ] Gate blocks only if post-fix verification still shows nonzero counts for severities in `failOn`.
- [ ] Artifacts clearly show pre-fix vs post-fix gate decision.

## Constraints
- Keep the additional review step lightweight/cost-aware (configurable if needed).

## References
- Seed: seed-add-retry-logic-on-failed-tickets
- Plan: plan-retry-logic-quality-gate-blocked


## Notes

**2026-02-10T13:41:39Z**

Implemented post-fix verification step for meaningful quality gates.

Changes:
- Added Post-Fix Verification procedure to tf-workflow skill
- Standardized fixes.md format with Summary Statistics section
- Quality gate now uses post-fix counts instead of pre-fix counts
- Created post_fix_verification.py with parsing and calculation logic

Commit: f68ec55
Artifacts: .tf/knowledge/tickets/pt-9uxj/
