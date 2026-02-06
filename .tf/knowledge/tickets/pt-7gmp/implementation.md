# Implementation: pt-7gmp

## Task
Add unit tests and minimal docs for `tf kb`.

## Acceptance Criteria
- [x] Tests cover: ls/show, archive/restore, delete, validate, rebuild-index.
- [x] Docs added to README or docs/commands.md.

## Approach

### Tests
Created `tests/test_kb_cli.py` with 32 comprehensive tests covering:

**cmd_ls (6 tests):**
- List all topics in human-readable format
- JSON output format
- Filter by topic type (seed, plan, spike, baseline)
- Include archived topics in listing
- Empty KB handling

**cmd_show (4 tests):**
- Show active topic details
- JSON output format
- Show archived topic details
- Handle non-existent topic

**cmd_archive (4 tests):**
- Archive active topic with reason
- Idempotent behavior (already archived)
- Removes from index.json
- Handle non-existent topic

**cmd_restore (4 tests):**
- Restore archived topic
- Idempotent behavior (already active)
- Adds back to index.json
- Handle non-existent topic

**cmd_delete (4 tests):**
- Delete active topic
- Delete archived topic
- Removes from index.json
- Handle non-existent topic

**cmd_validate (6 tests):**
- Valid KB passes
- Detect missing files
- Detect orphan directories
- Detect duplicate IDs
- JSON output format
- Handle missing index

**cmd_index_status (4 tests):**
- Show index status
- Show with archived topics count
- JSON output format
- Handle missing index

### Docs
Added comprehensive `tf kb` section to `docs/commands.md` with:
- Command syntax and all subcommands
- Global options table
- Usage examples for all commands
- Validation checks description

## Files Changed
- `tests/test_kb_cli.py` - New comprehensive test suite (32 tests, 474 lines)
- `docs/commands.md` - Added tf kb command reference section

## Test Results
```
79 passed in 0.46s
- test_kb_cli.py: 32 tests
- test_kb_helpers.py: 35 tests  
- test_kb_rebuild_index.py: 12 tests
```

## Verification
```bash
# Run all KB tests
cd /home/volker/coding/pi-ticketflow
source .venv/bin/activate
python -m pytest tests/test_kb_*.py -v
```
