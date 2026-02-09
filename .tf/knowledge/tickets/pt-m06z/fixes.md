# Fixes: pt-m06z

## Summary
Fixed all Critical and Major issues identified in review - corrected mock.patch() paths and incomplete imports to properly use `tf.*` namespace.

## Fixes Applied

### Critical (must fix)
1. **`tests/test_tags_suggest.py:11`** - Changed import from `from tf_cli import tags_suggest` to `from tf import tags_suggest`
2. **`tests/test_tags_suggest.py:1`** - Fixed docstring to reference `tf.tags_suggest` instead of `tf_cli.tags_suggest`

3. **`tests/test_track.py:38`** - Changed mock patch from `tf_cli.track.Path.cwd` to `tf.track.Path.cwd`
4. **`tests/test_track.py:44`** - Changed mock patch from `tf_cli.track.Path.cwd` to `tf.track.Path.cwd`
5. **`tests/test_track.py:57`** - Changed mock patch from `tf_cli.track.resolve_files_changed` to `tf.track.resolve_files_changed`
6. **`tests/test_track.py:71`** - Changed mock patch from `tf_cli.track.resolve_files_changed` to `tf.track.resolve_files_changed`
7. **`tests/test_track.py:84`** - Changed mock patch from `tf_cli.track.resolve_files_changed` to `tf.track.resolve_files_changed`
8. **`tests/test_track.py:96`** - Changed mock patch from `tf_cli.track.resolve_files_changed` to `tf.track.resolve_files_changed`
9. **`tests/test_track.py:97`** - Changed mock patch from `tf_cli.track.resolve_files_changed` to `tf.track.resolve_files_changed`
10. **`tests/test_track.py:109`** - Changed mock patch from `tf_cli.track.resolve_files_changed` to `tf.track.resolve_files_changed`

11. **`tests/test_sync.py:135`** - Changed mock patch from `tf_cli.project_bundle.install_bundle` to `tf.project_bundle.install_bundle`
12. **`tests/test_sync.py:144`** - Changed mock patch from `tf_cli.project_bundle.install_bundle` to `tf.project_bundle.install_bundle`

13. **`tests/test_cli_version.py:60`** - Changed mock patch from `tf_cli.version._resolve_repo_root` to `tf._resolve_repo_root`
14. **`tests/test_cli_version.py:102`** - Changed mock patch from `tf_cli.version._resolve_repo_root` to `tf._resolve_repo_root`
15. **`tests/test_cli_version.py:72`** - Changed mock patch from `tf_cli.cli.get_version` to `tf.get_version`
16. **`tests/test_cli_version.py:81`** - Changed mock patch from `tf_cli.cli.get_version` to `tf.get_version`
17. **`tests/test_cli_version.py:90`** - Changed mock patch from `tf_cli.cli.get_version` to `tf.get_version`
18. **`tests/test_cli_version.py:111`** - Changed mock patch from `tf_cli.cli.get_version` to `tf.get_version`

### Major (should fix)
19. **`tests/test_ticket_loader.py:1`** - Fixed docstring to reference `tf/ticket_loader.py` instead of `tf_cli/ticket_loader.py`
20. **`tests/test_topic_loader.py:1`** - Fixed docstring to reference `tf/ui.py` instead of `tf_cli/ui.py`

## Root Cause
When migrating imports from `from tf_cli import X` to `from tf import X`, mock.patch() calls must also be updated to use `tf.X.function` instead of `tf_cli.X.function`. This is because mock.patch() must patch where the function is looked up at runtime, which matches the import path.

## Verification
- All Python files compile successfully
- No `from tf_cli` imports remain in fixed test files
- No `tf_cli.*` mock patches remain in fixed test files
- Test imports resolve correctly

## Tests Status
- All files compile without errors
- Imports verified working

## Files Changed
- tests/test_tags_suggest.py
- tests/test_track.py
- tests/test_sync.py
- tests/test_cli_version.py
- tests/test_ticket_loader.py
- tests/test_topic_loader.py
