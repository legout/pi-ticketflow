# Implementation: ptw-xwlc

## Summary
Updated `/tf-backlog` workflow to automatically assign `component:*` tags to newly created tickets using the existing component classifier.

## Files Changed
- `prompts/tf-backlog.md` - Updated workflow documentation:
  - Changed `--no-component-tags` description from "Skip automatic component tag suggestion" to "Skip automatic component tag assignment"
  - Updated Step 8 from "Suggest component tags" to "Apply component tags by default"
  - Added detailed instructions for using `tf_cli.component_classifier.classify_components()`
  - Updated `tk create` examples to show `<component-tags>` placeholder
  - Added documentation for how tags are applied during ticket creation
  - Added fallback note about re-running tagging via `/tf-tags-suggest --apply`

## Key Decisions
- **Leveraged existing classifier**: The `tf_cli.component_classifier` module already exists with comprehensive keyword mappings and tests. Rather than creating new logic, the prompt now directs the agent to use this existing module.
- **Default-on behavior**: Component tagging is now enabled by default (opt-out via `--no-component-tags`), which matches the acceptance criteria for consistent component tags across tickets.
- **Conservative tagging**: Tickets without confident component matches are left untagged (no random tagging), satisfying the acceptance criteria for quality.

## Tests Run
- All 24 existing component classifier tests pass:
  ```
  tests/test_component_classifier.py::TestClassificationResult - PASSED
  tests/test_component_classifier.py::TestClassifyComponents - PASSED
  tests/test_component_classifier.py::TestFormatTagsForTk - PASSED
  tests/test_component_classifier.py::TestGetKeywordMapDocumentation - PASSED
  tests/test_component_classifier.py::TestDefaultKeywordMap - PASSED
  ```

## Verification
1. The updated prompt correctly documents the new default behavior
2. The `--no-component-tags` flag is documented for opt-out
3. Classifier integration instructions include proper Python imports and usage
4. Fallback workflow (`/tf-tags-suggest --apply`) is documented

## Acceptance Criteria Status
- [x] `/tf-backlog` assigns at least one `component:*` tag to each created ticket when it can infer one
- [x] Tickets without a confident component are left untagged (no random tagging)
- [x] Behavior is documented, including how to re-run tagging via `/tf-tags-suggest`
- [x] Existing `/tf-backlog` behavior is preserved (just adds tags by default)
