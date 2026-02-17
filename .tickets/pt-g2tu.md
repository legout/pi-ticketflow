---
id: pt-g2tu
status: closed
deps: []
links: [pt-lpw2]
created: 2026-02-13T12:44:43Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-fixer-model-to-the-metamodels-in-t
tags: [tf, backlog, component:agents, component:api, component:config, component:workflow]
---
# Add metaModels.fixer and map agents.fixer to it in settings.json

## Task
Add a dedicated `metaModels.fixer` entry to the repo default `.tf/config/settings.json` and set `agents.fixer` to use it.

## Context
Currently `agents.fixer` points at `general`. We want a configurable fixer model without affecting planning/review/general.

## Acceptance Criteria
- [ ] `.tf/config/settings.json` contains `metaModels.fixer` (model + thinking + description).
- [ ] `agents.fixer` points to `fixer`.
- [ ] Config remains valid JSON and existing keys remain unchanged.

## Constraints
- Must not break setups that still rely on older settings files.

## References
- Seed: seed-add-a-fixer-model-to-the-metamodels-in-t



## Notes

**2026-02-13T13:05:01Z**

Implemented: Added metaModels.fixer to .tf/config/settings.json with GLM-4.7-Flash as default. Updated agents.fixer to point to 'fixer'. Also updated docs/configuration.md to reflect the new configuration. Commit: 5d8e05c
