---
id: ptw-ztdh
status: closed
deps: []
links: []
created: 2026-02-05T14:00:22Z
type: task
priority: 2
assignee: legout
external-ref: seed-backlog-deps-and-tags
tags: [tf, backlog]
---
# Update tf-tags-suggest to share classifier logic

## Task
Refactor /tf-tags-suggest (or its underlying implementation) to reuse the same component classifier used by /tf-backlog.

## Context
The seed expects /tf-tags-suggest to remain the fallback when automatic tagging fails. To avoid divergence, both paths should share logic.

## Acceptance Criteria
- [ ] /tf-backlog and /tf-tags-suggest produce consistent `component:*` suggestions.
- [ ] Any shared logic is in a single module/file.
- [ ] Documentation updated to describe the relationship.

## Constraints
- Keep changes small and backwards compatible.

## References
- Seed: seed-backlog-deps-and-tags


## Notes

**2026-02-05T16:46:33Z**

Implemented documentation updates to clarify shared component classifier usage.

Changes:
- Updated tf_cli/component_classifier.py with module-level documentation explaining it's the shared source of truth
- Updated tf_cli/tags_suggest_new.py docstring to reference the shared classifier
- Updated docs/commands.md with 'Component Tag Assignment' and 'Shared Classifier' sections
- Updated prompts/tf-backlog.md to explicitly reference the shared module

All 24 existing tests pass. No functional changes - documentation only.

Commit: 58b77b0
