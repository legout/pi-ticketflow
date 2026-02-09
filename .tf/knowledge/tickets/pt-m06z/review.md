# Review: pt-m06z

## Overall Assessment
The implementation correctly migrates most test imports from `tf_cli.*` to `tf.*`, but contains **critical issues** with mock/patch paths. Several mock.patch() calls still reference the old `tf_cli.*` namespace even though the imports were changed to `tf.*`. This breaks tests because mock paths must match the import namespace being used.

## Critical (must fix)
- `tests/test_tags_suggest.py:11` - Import is `from tf_cli import tags_suggest` but should be `from tf import tags_suggest`
- `tests/test_track.py:38,44` - Mock patches use `tf_cli.track.Path.cwd` but should use `tf.track.Path.cwd`
- `tests/test_track.py:57,71,84,109` - Mock patches use `tf_cli.track.resolve_files_changed` but should use `tf.track.resolve_files_changed`
- `tests/test_track.py:96-97` - Mock patches use `tf_cli.track.*` but should use `tf.track.*`
- `tests/test_sync.py:135,144` - Mock patches use `tf_cli.project_bundle.install_bundle` but should use `tf.project_bundle.install_bundle`
- `tests/test_cli_version.py:60,102` - Mock patches use `tf_cli.version._resolve_repo_root` but should use `tf._resolve_repo_root`
- `tests/test_cli_version.py:72,81,90,111` - Mock patches use `tf_cli.cli.get_version` but should use `tf.get_version` or `tf.cli.get_version`

## Major (should fix)
- `tests/test_tags_suggest.py:1` - Docstring says "Tests for tf_cli.tags_suggest" but should say "Tests for tf.tags_suggest"
- `tests/test_ticket_loader.py:1` - Docstring references `tf_cli/ticket_loader.py` but should reference `tf/ticket_loader.py`
- `tests/test_topic_loader.py:1` - Docstring references `tf_cli/ui.py` but should reference `tf/ui.py`

## Minor (nice to fix)
- `tests/test_ui_smoke.py:43` - Has `from tf_cli import ui` inside test function (intentional for shim test, could clarify comment)
- `tests/test_doctor_version.py:4` - Comment says "in tf_cli/doctor.py" but should say "in tf/doctor.py"

## Warnings (follow-up ticket)
- `tests/test_cli_version.py` - This file was not tracked in implementation.md but has the same mock path issue

## Suggestions (follow-up ticket)
- Consider adding a CI check/linting rule to detect `tf_cli.*` imports in test files (excluding known shim tests)
- Document the migration pattern: when patching after `from tf import X`, use `tf.X.function` not `tf_cli.X.function`

## Positive Notes
- `test_tf_cli_shim.py` is excellent - comprehensive shim tests properly preserved
- `test_version.py` and `test_workflow_status.py` correctly preserved `tf_cli` imports
- Most test files (22+) were correctly migrated
- Implementation.md is well documented with clear reasoning

## Summary Statistics
- Critical: 17 (mock/patch path mismatches and incomplete imports)
- Major: 3 (inconsistent docstrings)
- Minor: 2 (cosmetic issues)
- Warnings: 1
- Suggestions: 2

## Review Sources
- reviewer-general: Found 16 critical mock path issues
- reviewer-second-opinion: Found incomplete test_tags_suggest.py migration
