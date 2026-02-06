# Implementation: pt-3nit

## Summary
Implemented `tf kb validate` command to detect knowledge base index drift.

## Files Changed
- `tf_cli/kb_cli.py` - Added `cmd_validate()` function and command dispatch

## Implementation Details

### New Function: `cmd_validate()`
Validates knowledge base integrity by checking:

1. **Missing files referenced by index entries** - Checks overview, sources, plan, backlog fields
2. **Orphan directories** - Detects dirs under `topics/*` not referenced in index
3. **Duplicate topic IDs** - Finds duplicate IDs in the index

### Output Formats
- **Human-readable**: Lists errors (✗) and warnings (⚠) with counts
- **JSON**: Structured output with all validation details

### Exit Codes
- `0` - No errors found (warnings don't fail)
- `1` - Errors detected or index not found

## Key Decisions
- Orphan directories are warnings (not errors) - allows flexibility in workflow
- Warnings don't affect exit code - only errors cause non-zero exit
- JSON output includes detailed structured data for programmatic use

## Verification
Tested scenarios:
1. ✓ Valid knowledge base (no issues)
2. ✓ Missing files referenced by index
3. ✓ Orphan directories not in index
4. ✓ Duplicate topic IDs
5. ✓ Missing index.json
6. ✓ JSON output format

## Tests
All 281 existing tests pass.
