# Review: pt-6rja

## Critical (must fix)
- `tf_cli/kb_cli.py:1` - Unused `argparse` import - module uses manual parsing but imports argparse unnecessarily
- `tf_cli/kb_cli.py:76-83` - Unused `_find_config_path()` function - defined but never called
- `tf_cli/kb_cli.py:225` - Logic error in `--knowledge-dir` parsing - searches `rest` without consuming value, loop continues unnecessarily

## Major (should fix)
- `tf_cli/kb_cli.py:178-180` / `kb_cli.py:191-193` - Double `--json` parsing bug - extracted in global parsing but checked again in `rest`
- `tf_cli/kb_cli.py:150-158` - Inconsistent exit codes - `cmd_index_status` returns 0 when index not found, `cmd_show` returns 1 in same scenario
- `tf_cli/kb_cli.py:175-176` - Inconsistent `--json` handling - `index` command doesn't support JSON output despite global flag

## Minor (nice to fix)
- `tf_cli/kb_cli.py:36-43` - Environment variable `TF_KNOWLEDGE_DIR` handling could validate path exists
- `tf_cli/kb_cli.py:115-125` - Project markers (tickets/, ralph/, bin/) may not match all valid project structures
- `tf_cli/kb_cli.py:196` - Error message for missing entry ID could show usage
- `tf_cli/kb_cli.py:130-135` / `kb_cli.py:165` - JSON decode error handling returns different exit codes (1 vs 0)
- `tf_cli/kb_cli.py:88-103` - Duplicated repo root logic exists in both `kb_cli.py` and `cli.py`

## Warnings (follow-up ticket)
- No test coverage for `kb_cli.py`
- Missing `--version` support unlike `new_cli.py`
- No JSON schema validation for index.json
- Manual arg parsing instead of argparse (inconsistent with `seed_cli.py`)
- Hardcoded project markers in `_find_repo_root()`

## Suggestions (follow-up ticket)
- Consider using `argparse` for better help text and validation
- Add autocomplete support for entry IDs
- Add `kb search` command for filtering
- Add colorized output support
- Cache resolved knowledge directory
- Validate knowledge directory exists with helpful error message

## Summary Statistics
- Critical: 3
- Major: 3
- Minor: 5
- Warnings: 4
- Suggestions: 5
