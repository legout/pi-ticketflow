---
id: pt-ctov
status: closed
deps: [pt-zwns]
links: [pt-gn5z]
created: 2026-02-06T13:51:23Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:agents, component:cli, component:docs, component:workflow]
---
# Document /tf-priority-reclassify and the P0–P4 rubric (README/docs)

## Task
Document the rubric and command usage (examples, dry-run vs apply, safety flags).

## Context
A shared rubric only works if it’s easy to find and consistently described.

## Acceptance Criteria
- [ ] README/docs include the P0–P4 rubric and examples.
- [ ] Prompt help text matches the implementation options.
- [ ] Notes on customizing/extending rules are included.

## Constraints
- Keep docs short; link to code for details.

## References
- Seed: seed-pi-command-reclassify-priorities


## Notes

**2026-02-06T14:31:32Z**

Documentation complete. Added P0-P4 rubric section to README, command reference to docs/commands.md, and updated prompt help text. Commit: 9b05606
