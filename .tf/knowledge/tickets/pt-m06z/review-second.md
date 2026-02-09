# Review (Second Opinion): pt-m06z

## Overall Assessment
The implementation correctly migrates most test imports from `tf_cli.*` to `tf.*` and preserves the shim tests. However, there are several incomplete migrations where mock patches still reference `tf_cli.*` paths instead of `tf.*`, which could cause test failures if the underlying implementation details change. The `test_tags_suggest.py` file was also not fully migrated.

## Critical (must fix)
- `tests/test_tags_suggest.py:11` - Still imports `from tf_cli import tags_suggest as tags_module` instead of `from tf import tags_suggest`. This is a direct import that should have been migrated per the ticket requirements. The file was marked as migrated in implementation.md but the primary import was not changed.

- `tests/test_track.py:38,44,57,71,84,96-97,109` - Mock patches still reference `tf_cli.track.*` paths instead of `tf.track.*`. When patching module-level functions, the patch path must match where the function is looked up at runtime. Since the test imports `from tf import track`, the patches should use `tf.track.resolve_files_changed` not `tf_cli.track.resolve_files_changed`.

- `tests/test_sync.py:135,144` - Mock patches reference `tf_cli.project_bundle.install_bundle` but should reference `tf.project_bundle.install_bundle` to match the import pattern `from tf import sync`.

## Major (should fix)
- `tests/test_cli_version.py` - Not mentioned in implementation.md but has the same issue: mock patches reference `tf_cli.cli.*` and `tf_cli.version.*` instead of `tf.cli.*` and `tf.version.*`. This file should either be listed as intentionally preserved (like test_version.py) or fully migrated with correct patch paths.

- `tests/test_tags_suggest.py:1` - Docstring still says "Tests for tf_cli.tags_suggest module" instead of "Tests for tf.tags_suggest module". While minor, this creates documentation drift.

## Minor (nice to fix)
- `tests/test_ui_smoke.py:43` - Contains `from tf_cli import ui` which tests the shim import. This is intentional per the test purpose (`test_ui_command_imports_module`), but it's inconsistent with the rest of the file which uses `from tf import ui`. Consider clarifying the test comment to explain this tests backward compatibility explicitly.

## Warnings (follow-up ticket)
- The implementation.md summary lists 24 test files as migrated, but `test_cli_version.py` is not included in any list (migrated, preserved, or already using tf.*). This suggests incomplete tracking of the test suite.

- The migration strategy for mock.patch paths should be documented: when patching where the imported module uses `from tf import X`, patches must use `tf.X.function` not `tf_cli.X.function`. This is a common pattern that will recur in future migrations.

## Suggestions (follow-up ticket)
- Consider adding a CI check or linting rule that detects `tf_cli.*` imports in test files (excluding test_tf_cli_shim.py, test_version.py, test_workflow_status.py) to prevent incomplete migrations in the future.

- Add documentation explaining the difference between:
  1. Importing from `tf_cli` to test shim functionality (valid, should be in test_tf_cli_shim.py only)
  2. Importing from `tf_cli` because module hasn't migrated yet (valid, documented)
  3. Incomplete migration leaving `tf_cli` references (invalid, should be caught)

## Positive Notes
- The shim regression tests in `test_tf_cli_shim.py` are comprehensive and correctly preserved, covering imports, re-exports, version matching, and deprecation warning behavior.
- `test_version.py` and `test_workflow_status.py` correctly preserve `tf_cli` imports as documented, since those modules haven't been migrated yet.
- Most test files (22 out of 24 listed) were successfully migrated to use `tf.*` imports.
- The test suite passes with the current implementation, indicating the shim is working correctly for runtime functionality.

## Summary Statistics
- Critical: 3
- Major: 2
- Minor: 1
- Warnings: 2
- Suggestions: 2
