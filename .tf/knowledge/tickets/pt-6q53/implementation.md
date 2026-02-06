# Implementation: pt-6q53

## Task
Implement `tf kb rebuild-index` to regenerate `index.json` from filesystem.

## Acceptance Criteria
- [x] Scans `.tf/knowledge/topics/*` and produces canonical index entries.
- [x] Stable ordering by topic id.
- [x] `--dry-run` prints changes without writing.
- [x] Default writes atomically.

## Implementation Plan

### 1. Add `cmd_rebuild_index` function to `kb_cli.py`

The command will:
1. Scan all topic directories under `{knowledge_dir}/topics/`
2. For each topic, extract metadata from frontmatter or existing index entry
3. Build canonical index entries with stable ordering by topic ID
4. Support `--dry-run` to preview changes
5. Use atomic write via `atomic_write_index()`

### 2. Update `usage()` to document the new command

### 3. Update `main()` to dispatch the new command

## Changes Made

### File: `tf_cli/kb_cli.py`

Added `cmd_rebuild_index()` function that:
- Discovers all topic directories
- Preserves existing metadata from current index when available
- Extracts title from frontmatter or existing index entry
- Generates stable sorted output by topic ID
- Shows diff-like output in dry-run mode
- Performs atomic write when not in dry-run mode

Added helper `_extract_title_from_frontmatter()` that:
- Extracts title from frontmatter field or first # heading
- Checks docs in priority order: overview.md, plan.md, sources.md, backlog.md

Updated `usage()` to include:
```
tf kb rebuild-index [--dry-run] [--knowledge-dir <path>]
```

Updated `main()` to:
- Parse `--dry-run` flag
- Dispatch to `cmd_rebuild_index()`

### File: `tests/test_kb_rebuild_index.py` (new)

Added comprehensive test suite with 14 tests:
- Title extraction from frontmatter and headings
- Dry-run mode with text and JSON output
- Index creation and stable ordering
- Metadata preservation
- Stale path removal
- Error handling for missing topics directory

## Key Decisions

1. **Metadata preservation**: When rebuilding, we preserve existing metadata from the current index (keywords, overview, sources paths) to avoid losing data.

2. **Title extraction**: If a topic exists in the current index, we use its title. Otherwise, we extract from the first # heading, falling back to frontmatter title field.

3. **Stable ordering**: Topics are sorted by ID to ensure deterministic output.

4. **Dry-run output**: Shows added, removed, and unchanged topics for clarity. JSON mode available for programmatic use.

5. **Atomic write**: Uses existing `atomic_write_index()` helper for safety.

## Test Results

All 295 tests pass:
- 33 tests in `test_kb_helpers.py` (existing)
- 14 new tests in `test_kb_rebuild_index.py`
- 248 other existing tests

## Verification

Tested manually:
```bash
# Dry-run mode
$ python -m tf_cli.cli kb rebuild-index --dry-run
Dry-run: Would rebuild index at /home/volker/coding/pi-ticketflow/.tf/knowledge/index.json
  Current topics: 7
  New topics: 7
  Unchanged (7):
    = plan-auto-planning-sessions-linkage
    ...

# JSON output
$ python -m tf_cli.cli kb rebuild-index --dry-run --json
{ "dry_run": true, "proposed_index": {...} }

# Actual rebuild
$ python -m tf_cli.cli kb rebuild-index
Rebuilt index: 7 topics

# Validate result
$ python -m tf_cli.cli kb validate
Knowledge base validation: PASSED
```
