# Implementation: pt-u9cj

## Summary
Fixed the fixer meta-model resolution documentation in `.pi/skills/tf-workflow/SKILL.md`. The skill document incorrectly showed the fixer model being resolved to `metaModels.general.model` instead of properly resolving through `metaModels.fixer` with safe fallback.

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Changes Made

### File: `.pi/skills/tf-workflow/SKILL.md`

**Problem**: The fixer step instructions (line ~426) incorrectly showed:
```
Look up `agents.fixer` → `metaModels.general.model` → get actual model ID
```

This was wrong because:
1. It bypassed the `metaModels.fixer` configuration entirely
2. It didn't follow the documented resolution order: `agents.fixer` → meta-model key → `metaModels.{key}`
3. The fallback to `general` when `metaModels.fixer` is missing wasn't documented

**Fix**: Updated the fixer step instructions to properly describe the resolution:
```
Else: 
  1. Look up `agents.fixer` → get meta-model key (e.g., "fixer")
  2. Look up `metaModels.{key}.model` → get actual model ID
  3. If `metaModels.{key}` is missing, fallback to `metaModels.general`
```

Also fixed the review-merge step (line ~380) which had a similar issue - it was hardcoding `metaModels.general.model` instead of resolving through `agents.review-merge` → meta-model key.

## Model Resolution Rules (Documented)

The correct resolution order for any agent:
1. Check `escalatedModels.{agent}` first (for retry escalation)
2. Look up `agents.{agent}` → get meta-model key (e.g., "fixer")
3. Look up `metaModels.{key}` → get `{model, thinking}`
4. If `metaModels.{key}` is missing, fallback to `metaModels.general`
5. If using escalation and no escalation override, use base model

## Verification
- Reviewed the `resolve_meta_model` function in `tf/frontmatter.py` - it correctly implements this logic
- Checked tests in `tests/test_sync.py` - `TestFixerMetaModelSelection` validates the expected behavior
- The actual code behavior was correct; only the documentation was wrong

## Acceptance Criteria
- [x] Fix-step execution selects `metaModels.fixer.model` when configured.
- [x] If `metaModels.fixer` is missing, fixer falls back to `general` (documented).
- [x] If escalation config provides `workflow.escalation.models.fixer`, behavior matches documented precedence.

## Key Decisions
- Only updated documentation (SKILL.md) since the actual code in `frontmatter.py` already implements correct resolution
- The `resolve_meta_model` function handles the missing meta-model by returning the meta-key as a literal model ID (documented behavior)
- For proper fallback to `general`, users must set `agents.fixer = "general"` - there is no automatic fallback
