---
id: pt-zwns
status: closed
deps: [pt-6ztc]
links: [pt-xue1]
created: 2026-02-06T13:51:23Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:cli, component:tests, component:workflow]
---
# Test priority reclassify: classifier rules + apply mode (tmp tickets)

## Task
Add pytest coverage for the classifier and the apply-mode frontmatter patching.

## Context
We need confidence that reclassification won’t corrupt ticket files and that rules behave deterministically.

## Acceptance Criteria
- [ ] Unit tests for rubric mapping + keyword rules.
- [ ] Tests that patching preserves unrelated frontmatter fields.
- [ ] Integration-style test with a temporary `.tickets/` directory.

## Constraints
- Tests must not modify real repo tickets.

## References
- Seed: seed-pi-command-reclassify-priorities

