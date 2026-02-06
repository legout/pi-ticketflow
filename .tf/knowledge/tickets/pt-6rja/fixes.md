# Fixes: pt-6rja

## Issues Fixed

### Critical
1. **Removed unused `argparse` import** - Line 9: Deleted `import argparse` since module uses manual parsing
2. **Removed unused `_find_config_path()` function** - Lines 66-76: Deleted entire unused function
3. **Fixed `--knowledge-dir` parsing logic** - Removed redundant second check in `rest` variable, now only parsed once in global flags loop

### Major
4. **Fixed double `--json` parsing bug** - Removed redundant `"--json" in rest` checks from `ls` and `show` commands, now uses only the `format_json` variable set during global parsing
5. **Fixed inconsistent exit codes** - `cmd_index_status` now returns 1 (error) when index not found or on JSON decode error, consistent with `cmd_show`
6. **Added JSON support to `index` command** - `cmd_index_status` now accepts `format_json` parameter and outputs JSON when requested

## Verification

```bash
# Test index without JSON (index exists)
$ python -m tf_cli.cli kb index
Knowledge base index: OK
Path: /home/volker/coding/pi-ticketflow/.tf/knowledge/index.json
Entries: 0
Exit code: 0

# Test index with JSON
$ python -m tf_cli.cli kb index --json
{"status": "ok", "path": "/home/volker/coding/pi-ticketflow/.tf/knowledge/index.json", "entries": 0}

# Test ls with JSON
$ python -m tf_cli.cli kb ls --json
{"entries": []}

# Test show with non-existent entry (returns 1)
$ python -m tf_cli.cli kb show missing-id 2>/dev/null
echo $?
1
```

## Files Modified
- `tf_cli/kb_cli.py` - Applied all fixes

## No Changes Required
- `tf_cli/cli.py` - No changes needed, dispatch logic was correct
