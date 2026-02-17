---
id: pt-te9b
status: closed
deps: []
links: [pt-xu9u]
created: 2026-02-10T12:39:47Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-retry-logic-on-failed-tickets
tags: [tf, backlog, component:api, component:config, component:docs, component:tests, component:workflow]
---
# Define retry state + quality-gate block detection

## Task
Define how we detect and persist retry attempts for tickets that fail to close due to the quality gate.

## Context
Ralph can repeatedly pick the same ticket when it remains open due to quality-gate `failOn` severities. We need deterministic detection of BLOCKED closes and durable retry state.
This backlog is derived from an approved plan (plan-retry-logic-quality-gate-blocked, status=approved).

## Acceptance Criteria
- [ ] A retry state file location is finalized (recommended: `.tf/knowledge/tickets/<id>/retry-state.json`).
- [ ] Detection algorithm is specified (prefer: parse `close-summary.md` status=BLOCKED; fallback to `review.md` failOn counts).
- [ ] Reset policy is specified (reset on successful close only).

## Constraints
- Must be safe under Ralph restarts.
- Must not leak secrets in artifacts/logs.

## References
- Seed: seed-add-retry-logic-on-failed-tickets
- Plan: plan-retry-logic-quality-gate-blocked


## Notes

**2026-02-10T12:45:07Z**

Design complete. Retry state specification defined with:

1. **Location**: .tf/knowledge/tickets/{id}/retry-state.json
2. **Schema**: Versioned JSON with attempts array, quality gate tracking, escalation config
3. **Detection**: Primary (close-summary.md BLOCKED status) + Fallback (review.md failOn counts)
4. **Reset Policy**: Reset only on successful close (CLOSED/COMPLETE status)
5. **Escalation Curve**: Tiered (Attempt 1=base, 2=fixer only, 3+=full escalation)
6. **Parallel Safety**: Documented assumption of ralph.parallelWorkers=1

Full spec: .tf/knowledge/tickets/pt-te9b/retry-state-spec.md
Commit: 2e43496

Review: 0 Critical, 0 Major issues. Ready to unblock pt-xu9u.
