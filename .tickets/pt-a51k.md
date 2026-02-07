---
id: pt-a51k
status: closed
deps: [pt-ynqf]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:cli, component:config]
---
# CLN-07: Consolidate frontmatter/model-sync logic into one implementation path

## Task
Unify duplicated model/frontmatter sync logic used by sync/config tooling.

## Context
Model sync logic currently exists in multiple places and can drift.

## Acceptance Criteria
- [ ] Single source of truth for frontmatter update behavior
- [ ] Duplicate implementations removed or reduced to wrappers
- [ ] tf sync behavior validated by tests

## Constraints
- Preserve config compatibility

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T15:53:49Z**

--message Implementation complete.

Consolidated frontmatter/model-sync logic into tf_cli/frontmatter.py:
- Created new shared module with resolve_meta_model(), update_frontmatter_fields(), update_agent_frontmatter(), update_prompt_frontmatter(), sync_models_to_files()
- Refactored tf_cli/sync_new.py to use shared module (-86 lines)
- Refactored scripts/tf_config.py to use shared module (-150 lines)
- Updated bundle copy .tf/scripts/tf_config.py
- All 15 tests in tests/test_sync_new.py pass
- Full backward compatibility preserved

Review results: 0 Critical, 0 Major, 3 Minor, 1 Warning, 5 Suggestions
No fixes required.

Commit: 6ad30b4
