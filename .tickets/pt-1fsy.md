---
id: pt-1fsy
status: closed
deps: [pt-qqwc]
links: [pt-qqwc]
created: 2026-02-06T13:51:23Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:cli, component:docs, component:tests, component:workflow]
---
# Implement rubric-based priority classifier + rationale generation

## Task
Implement deterministic rubric rules that propose P0–P4 (and tk priority 0–4) plus a short explanation per ticket.

## Context
We need explainable results so humans can trust the automated reclassification during backlog grooming.

## Acceptance Criteria
- [ ] Rules cover: security, data correctness, OOM/resource risk, product features, eng quality/workflow, cosmetics/docs.
- [ ] Output includes: current priority, proposed priority, rubric bucket, and reason.
- [ ] Ambiguous tickets return “unknown” and are skipped by default.

## Constraints
- Keep rules conservative (prefer unknown over wrong changes).

## References
- Seed: seed-pi-command-reclassify-priorities


## Notes

**2026-02-06T14:12:47Z**

## Implementation Complete

Implemented rubric-based priority classifier with comprehensive P0-P4 classification rules:

**Changes:**
- Complete rewrite of 
- Added comprehensive rubric covering: security, data correctness, OOM/resource risk, product features, eng quality/workflow, cosmetics/docs
- Output includes: current priority, proposed priority, rubric bucket, and reason
- Ambiguous tickets return 'unknown' and are skipped by default (use --include-unknown to show)
- Added ClassificationResult dataclass with confidence levels
- Maintained backward compatibility with existing test expectations

**Rubric Categories:**
- P0 (critical-risk): security, data loss, crashes, compliance
- P1 (high-impact): user bugs, performance, release blockers
- P2 (product-feature): standard features, integrations
- P3 (engineering-quality): refactors, DX, CI/CD
- P4 (maintenance-polish): docs, cosmetics, typing

**Commit:** e642d18
**Tests:** All 372 tests passing
