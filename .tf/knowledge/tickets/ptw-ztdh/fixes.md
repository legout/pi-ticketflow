# Fixes: ptw-ztdh

## Summary
No fixes needed. This was a documentation-only change to clarify the relationship between `/tf-backlog` and `/tf-tags-suggest` through the shared `component_classifier` module.

## Files Modified
Documentation updates only:
1. `tf_cli/component_classifier.py` - Added module-level documentation
2. `tf_cli/tags_suggest_new.py` - Updated module docstring
3. `docs/commands.md` - Added relationship documentation
4. `prompts/tf-backlog.md` - Updated classifier reference

## Verification
- All 24 existing tests pass
- No functional changes to classification logic
- Changes are purely additive (documentation)
