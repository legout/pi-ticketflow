# Review: pt-u9cj

## Overall Assessment
This ticket corrected documentation in `.pi/skills/tf-workflow/SKILL.md` to accurately describe the fixer meta-model resolution. The documentation now correctly shows that the resolution goes through `agents.fixer` → meta-model key → `metaModels.{key}` instead of incorrectly jumping directly to `metaModels.general`. However, there remain subtle documentation ambiguities and potential edge case mismatches between the documented fallback behavior and the actual implementation that could confuse users.

## Critical (must fix)
- `SKILL.md:430` - The documentation states "If `metaModels.{key}` is missing, fallback to `metaModels.general`" which is **factually incorrect**. The actual `resolve_meta_model` code in `tf/frontmatter.py` (lines 38-39) returns `{"model": meta_key, "thinking": "medium"}` using the meta-key as a literal model ID, NOT `metaModels.general`. This discrepancy could lead users to believe the system automatically falls back to the general model, when in reality it would attempt to use a model named after the meta-key (e.g., model ID "fixer"), which likely doesn't exist and would cause runtime failures. The documentation must be corrected to match the implementation: either document the actual behavior (meta-key as literal model ID) or the implementation should be changed to match the documentation (automatic fallback to general). Given the tests in `tests/test_sync.py::TestFixerMetaModelSelection::test_fixer_fallback_when_meta_model_missing` explicitly expect the "meta-key as literal model" behavior, the documentation is wrong.

## Major (should fix)
- `SKILL.md:382-383` - The review-merge step still hardcodes `metaModels.general.model` in the example. While step 2 says "Look up `agents.review-merge` in config → get meta-model key ("general")" (note the quoted "general" assumption), the variable nature of the configuration should be clearer. The step should follow the same pattern as the fixer step: store the meta-key in a variable and look up `metaModels.{key}.model`. The current wording assumes `agents.review-merge` will always be "general" and doesn't demonstrate the proper resolution pattern that allows flexibility.
- `SKILL.md:428` - Step 2 says "Look up `metaModels.{key}` → get model settings" but should explicitly say "Look up `metaModels.{key}.model` → get actual model ID" to match the code's usage (the resolve function returns a dict with 'model' and 'thinking'). Saying "model settings" is vague; the switch_model call needs just the model ID string.
- `SKILL.md:380-382` and `SKILL.md:427-430` - Both the review-merge and fixer steps describe a three-step resolution but omit the **first** rule from the documented resolution order in the Configuration section: escalation overrides (`escalatedModels.{agent}`) take precedence. The fixer step mentions "If `escalatedModels.fixer` is set" as a separate bullet, but the review-merge step doesn't mention escalation at all. For consistency and completeness, all model resolution steps should either reference the main "Model resolution order" documentation or explicitly include the escalation check.

## Minor (nice to fix)
- `SKILL.md:427` - The example `(e.g., "fixer")` for the meta-model key could be misleading. If `agents.fixer = "fixer"`, then the meta-model key is indeed "fixer", but this is just a default/convention. The example might be clearer as `(e.g., the value from agents.fixer, such as "fixer" or "general")`.
- `SKILL.md:431` - The line `switch_model action="switch" search="{fixer_model_id}"` uses a placeholder that's not defined in the preceding steps. The steps should define `{fixer_model_id}` as the result of step 2 or the fallback in step 3. For example: "→ `{fixer_model_id} = metaModels.{key}.model`" or "→ `{fixer_model_id} = metaModels.general.model` if fallback". The current placeholder might be confusing without showing its assignment.
- `SKILL.md:1-520` - The document overall is extremely long (over 500 lines), making maintenance error-prone. Consider breaking it into separate linked documents (e.g., RE-ANCHOR.md, IMPLEMENT.md, REVIEW.md, FIX.md, CLOSE.md) with a main SKILL.md that links to them. This would reduce the surface area for inconsistencies like the one fixed here.

## Warnings (follow-up ticket)
- `SKILL.md` vs `tf/frontmatter.py` behavior divergence: The skill documentation describes a fallback to `metaModels.general`, but the implementation uses "meta-key as literal model ID". This is a **design-level mismatch** that could be intentional (documented fallback pattern) or an oversight. If intentional, the code comment in `frontmatter.py` should be updated to explain why this fallback exists and guide users to use `agents.fixer="general"` instead of expecting automatic fallback. If unintentional, a separate ticket should fix the code to match the documentation (change `resolve_meta_model` to fallback to `metaModels.general` when the specific meta-model is missing). The tests would need updating accordingly.
- `tests/test_sync.py::TestFixerMetaModelSelection` - The test `test_fixer_fallback_when_meta_model_missing` expects `{"model": "fixer", ...}` which matches the current implementation. If the documentation is considered authoritative, the test would be wrong. Conversely, if the implementation is authoritative, the documentation is wrong. This alignment issue needs a decision: either update the docs to match tests, or update the code+tests to match an automatic-fallback-to-general design. The current ticket only fixed the doc to match the code? Not entirely - the doc still says fallback to general, which doesn't match the test's expectation. So the fix is incomplete.

## Suggestions (follow-up ticket)
- `tf/frontmatter.py:38-39` - Add a detailed comment explaining the fallback behavior: "If the configured meta-model key is not defined in metaModels, we return the meta-key itself as the model ID. This allows explicit fallback configuration via agents.{name} = 'general' rather than implicit magic fallback. Users must define metaModels.{key} or point agents.{name} to an existing meta-model key."
- `SKILL.md:350-360` (Configuration section) - Expand the "Model resolution order" to include the full precedence: (1) escalatedModels, (2) agents → metaModels, (3) fallback. Also explicitly document the fallback behavior: "If `metaModels.{key}` is missing, the meta-key is used as a literal model ID (which will likely fail unless that model exists). To use the general model, set `agents.{name} = 'general'`."
- Create a separate `MODEL_RESOLUTION.md` design document that explains the resolution algorithm, edge cases, and retry escalation in one place, then link to it from SKILL.md and ensure all procedure steps reference it consistently.

## Positive Notes
- The documentation fix correctly removed the hardcoded `metaModels.general` reference in the primary fixer resolution path, now using a variable `{key}` derived from `agents.fixer`. This prevents the misconception that the fixer always uses the general model.
- The implementation note in `implementation.md` clearly explains the reasoning: the code was already correct, only the documentation needed updating. It also correctly notes that users should define `metaModels.fixer` or set `agents.fixer="general"` for proper fallback.
- The test suite covers the key behaviors, including the fallback case and escalation overrides, providing confidence that the implementation is well-specified.
- The integration with the retry escalation system appears thoughtful, with proper mapping between camelCase config keys and hyphenated agent names.

## Summary Statistics
- Critical: 1
- Major: 4
- Minor: 4
- Warnings: 2
- Suggestions: 3
