---
id: pt-psvv
status: closed
deps: [pt-1fsy]
links: [pt-xue1]
created: 2026-02-06T13:51:23Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:api, component:cli, component:config, component:docs, component:workflow]
---
# Implement dry-run output + optional reclassify report artifact

## Task
Add dry-run output that summarizes proposed priority changes, and optionally write a markdown/JSON report for review.

## Context
Dry-run should be the default mode. A report artifact helps review changes before applying.

## Acceptance Criteria
- [ ] Human-readable table printed (id, title, current, proposed, reason).
- [ ] Optional `--json` output for scripting.
- [ ] Optional report file written under `.tf/knowledge/` (path documented).

## Constraints
- Report must not contain secrets; only ticket metadata.

## References
- Seed: seed-pi-command-reclassify-priorities


## Notes

**2026-02-06T14:15:06Z**

Implemented dry-run output features:

- Added --json flag for JSON output (scripting-friendly)
- Added --report flag to optionally write report to .tf/knowledge/priority-reclassify-{timestamp}.md
- Human-readable table remains default output format
- All 30 tests passing

Commit: 3986649
