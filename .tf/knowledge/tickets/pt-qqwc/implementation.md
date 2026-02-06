# Implementation: pt-qqwc

## Summary
Implemented ticket selection for priority reclassify command (`tf priority-reclassify`). Added the `--include-closed` flag to allow including closed tickets in processing.

## Files Changed
- `tf_cli/priority_reclassify_new.py` - Added `--include-closed` flag
- `tests/test_priority_reclassify.py` - Comprehensive test suite for the feature

## Key Decisions
1. The ticket selection functionality (`--ids`, `--ready`, `--status`, `--tag`) was already implemented in `priority_reclassify_new.py`
2. Only missing piece was the `--include-closed` flag to override the default exclusion of closed tickets
3. Added comprehensive test coverage with 26 tests covering:
   - Ticket parsing
   - Priority classification (P0-P4 rubric)
   - All ticket selection methods (--ids, --ready, --status, --tag)
   - Closed ticket handling (excluded by default, included with flag)
   - Audit trail writing
   - CLI argument parsing

## Acceptance Criteria Verification
- ✅ Supports explicit ticket IDs (partial IDs allowed via `tk show`)
- ✅ Supports `--ready` (uses `tk ready`)
- ✅ Supports `--status` for status filtering
- ✅ Supports `--tag` for tag filtering  
- ✅ Excludes closed tickets by default
- ✅ Can include closed tickets with `--include-closed` flag
- ✅ Read-only when `--apply` is not set (dry-run by default)

## Tests Run
```bash
$ .venv/bin/python -m pytest tests/test_priority_reclassify.py -v
26 passed

$ .venv/bin/python -m pytest tests/ -v
372 passed
```

## Verification
Test the command:
```bash
# Show help with all selection options
tf priority-reclassify --help

# Process specific tickets (dry-run)
tf priority-reclassify --ids abc-1234,def-5678

# Process ready tickets
tf priority-reclassify --ready

# Process tickets by status
tf priority-reclassify --status open

# Process tickets by tag
tf priority-reclassify --tag bug

# Include closed tickets
tf priority-reclassify --ready --include-closed
```