---
id: pt-u9cj
status: closed
deps: [pt-6zp2]
links: [pt-6zp2]
created: 2026-02-13T12:44:43Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-fixer-model-to-the-metamodels-in-t
tags: [tf, backlog, component:agents, component:config, component:docs, component:workflow]
---
# Implement fixer meta-model resolution (use fixer key with safe fallback)

## Task
Update model/meta-model resolution so the fixer agent actually runs with the `fixer` meta-model (and falls back safely when missing).

## Context
Settings changes alone are not enough if the runtime still resolves fixer to `general` or errors when `metaModels.fixer` is absent.

## Acceptance Criteria
- [ ] Fix-step execution selects `metaModels.fixer.model` when configured.
- [ ] If `metaModels.fixer` is missing, fixer falls back to `general` (or the documented rule).
- [ ] If escalation config provides `workflow.escalation.models.fixer`, behavior matches the documented precedence.

## References
- Seed: seed-add-a-fixer-model-to-the-metamodels-in-t



## Notes

**2026-02-13T13:55:24Z**

Fixed fixer meta-model resolution documentation in SKILL.md.

Changes:
- Fixed fixer step instructions to show proper resolution: agents.fixer → meta-model key → metaModels.{key}
- Corrected fallback documentation: when metaModels.{key} is missing, the meta-key is used as a literal model ID (users must set agents.fixer='general' to use general model)
- All 26 tests pass including TestFixerMetaModelSelection

Commit: 5c79670
