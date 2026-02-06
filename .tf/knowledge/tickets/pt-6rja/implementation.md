# Implementation: pt-6rja

## Summary
Added Python CLI dispatch for `tf kb` commands, routing knowledge-base commands through the Python CLI (`tf_cli/cli.py`) without depending on the legacy shell script.

## Files Changed
- `tf_cli/kb_cli.py` - New module implementing kb subcommands (ls, show, index)
- `tf_cli/cli.py` - Added dispatch for `kb` command to kb_cli module

## Key Decisions
- Created `kb_cli.py` following the same pattern as `new_cli.py` and `seed_cli.py`
- Implemented three initial commands: `ls`, `show`, and `index`
- Added `--knowledge-dir` override flag for flexibility
- Added `--json` output format option for scripting
- Implemented proper knowledge directory resolution:
  1. Explicit `--knowledge-dir` flag
  2. `TF_KNOWLEDGE_DIR` environment variable
  3. Local `.tf/config/settings.json` (workflow.knowledgeDir)
  4. Auto-detected repo root + `.tf/knowledge`
- Repo root detection uses project-specific markers (tickets/, ralph/, bin/, pyproject.toml + AGENTS.md) to avoid matching global ~/.tf

## Tests Run
```bash
# Test 1: Direct Python module execution
$ python -m tf_cli.cli kb --help
# Output: Usage information displayed ✓

# Test 2: Via bin/tf shim
$ ./bin/tf kb --help
# Output: Usage information displayed ✓

# Test 3: List command (empty knowledge base)
$ python -m tf_cli.cli kb ls
# Output: "Knowledge base is empty." ✓

# Test 4: Index status
$ python -m tf_cli.cli kb index
# Output: Shows index status with correct path ✓

# Test 5: Show non-existent entry
$ python -m tf_cli.cli kb show test-entry
# Output: Error message, exit code 1 ✓
```

## Verification
All acceptance criteria met:
- [x] `python -m tf_cli.cli kb --help` works
- [x] `tf kb --help` works when running via `bin/tf` shim
- [x] No legacy script invocation is required for kb

## Notes
- The knowledge base index.json doesn't exist yet (separate ticket pt-fsk3 handles index.json IO)
- Additional kb subcommands (add, remove, update) can be added to kb_cli.py as needed
- The module structure supports easy extension for future kb management features
