---
id: pt-6ztc
status: closed
deps: [pt-xue1]
links: []
created: 2026-02-06T13:51:23Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:cli, component:workflow]
---
# Add safety UX: confirmation, change limits, and skip/force controls

## Task
Add guardrails so priority changes are hard to do accidentally and easy to review.

## Context
Priority reclassification can be disruptive. The command should default to safe behavior and require explicit confirmation.

## Acceptance Criteria
- [ ] `--apply` requires `--yes` (or interactive confirmation when TTY).
- [ ] Supports `--max-changes N` to cap updates.
- [ ] Supports `--force` (apply even when ambiguous) and default skip for unknown.

## Constraints
- Prefer under-changing over over-changing.

## References
- Seed: seed-pi-command-reclassify-priorities


## Notes

**2026-02-06T14:23:05Z**

Implementation complete: Added safety UX guardrails to priority reclassify command

Changes:
- --apply requires --yes in non-interactive mode (or interactive confirmation when TTY)
- --max-changes N caps the number of tickets that will be modified
- --force allows applying changes even for ambiguous/unknown classifications
- 36 tests passing

Commit: 44335a4
