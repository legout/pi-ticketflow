# Review: pt-u9cj

## Overall Assessment
Document clean-up around model resolution clarifies the review and fix procedures, but the new fixer fallback wording is still inaccurate with respect to the resolver logic and accompanying tests. Because the resolver treats a missing meta-model as a literal model name, the docs should not promise a general fallback the code does not provide. This mismatch risks misconfigured fixers and blocked ticket runs.

## Critical (must fix)
- No issues found

## Major (should fix)
- .pi/skills/tf-workflow/SKILL.md:424-429 - The Fix Issues procedure now states “If `metaModels.{key}` is missing, fallback to `metaModels.general`,” but `tf/frontmatter.py:33-45` (and `tests/test_sync.py:216-233`) show that the resolver instead treats the meta-model key as a literal model ID unless the agent is explicitly remapped to “general”. Users following the doc would omit `metaModels.fixer` expecting `general` to be used and the runtime will attempt to switch to `model="fixer"`, a model that doesn’t exist, breaking the fixer step. Please revert to documenting the literal-key fallback or adjust the implementation accordingly.

## Minor (nice to fix)
- No issues found

## Warnings (follow-up ticket)
- No issues found

## Suggestions (follow-up ticket)
- No issues found

## Positive Notes
- The merge step now explicitly traces `agents.review-merge` → meta-model key → `metaModels.general`, which makes the flow easier to follow.

## Summary Statistics
- Critical: 0
- Major: 1
- Minor: 0
- Warnings: 0
- Suggestions: 0
