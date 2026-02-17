---
id: pt-lw9p
status: closed
deps: [pt-lpw2]
links: [pt-lpw2, pt-6zp2]
created: 2026-02-13T12:44:43Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-fixer-model-to-the-metamodels-in-t
tags: [tf, backlog, component:agents, component:api, component:config, component:docs, component:tests, component:workflow]
---
# Define fixer meta-model selection rules (fallback + escalation)

## Task
Define and document how the workflow chooses the model for the **fixer** step.

## Context
We want to introduce `metaModels.fixer` in `.tf/config/settings.json`, but need clear rules for fallback and how it interacts with `workflow.escalation.models.fixer`.

## Acceptance Criteria
- [ ] Rules are written down (doc or code comments): precedence + fallback behavior.
- [ ] Backward compatibility decision recorded (when `metaModels.fixer` is missing).
- [ ] Any ambiguous behavior is covered by a test plan (what cases must be tested).

## Constraints
- Keep scope to 1–2h; defer non-essential refactors.

## References
- Seed: seed-add-a-fixer-model-to-the-metamodels-in-t



## Notes

**2026-02-13T13:24:50Z**

Implemented: Created comprehensive design document defining fixer meta-model selection rules (precedence, fallback, escalation). Fixed bug in tf/frontmatter.py where fallback used agent name instead of meta-model key. Added 4 new test cases for fallback behavior. Commit: 5d9079b
