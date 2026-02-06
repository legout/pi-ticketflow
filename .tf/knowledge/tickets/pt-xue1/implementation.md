# Implementation: pt-xue1

## Summary
Implemented the `--apply` mode for `tf priority-reclassify` command that updates ticket frontmatter priority safely and records an audit note.

## Files Changed
- `tf_cli/priority_reclassify_new.py` - Added apply mode functionality:
  - `get_tickets_dir()` - Get the tickets directory path
  - `parse_frontmatter()` - Parse YAML frontmatter from ticket content
  - `update_frontmatter_priority()` - Update priority field while preserving format
  - `add_note_to_ticket_body()` - Add audit note with timestamp
  - `update_ticket_priority()` - Main function to update ticket and add note
  - Updated `main()` to actually apply changes when `--apply` flag is set

## Key Decisions
1. **Direct file modification**: Since tickets are local markdown files, the implementation directly modifies the `.tickets/{id}.md` files rather than using a `tk` subcommand.

2. **Atomic writes**: Uses a temp file + rename pattern to ensure atomic updates and prevent data corruption.

3. **Git-friendly changes**: The implementation preserves the original file format, only changing the priority field and adding notes. This makes diffs clean and reviewable.

4. **Audit trail**: Each change adds a note under `## Notes` section with:
   - ISO timestamp
   - Old → New priority
   - Reason for reclassification

5. **Error handling**: Tracks failed updates and reports them to stderr without failing the entire batch.

## Acceptance Criteria Verification

- [x] `--apply` updates `priority:` for selected tickets (only when proposed != current)
- [x] A backup/reversible change strategy exists (git diff friendly, atomic writes)
- [x] Adds a note describing old→new + reason
- [x] Does not change closed tickets unless `--include-closed` is set

## Tests Run
```bash
pytest tests/test_priority_reclassify.py -v  # 30 passed
pytest tests/ -v                               # 376 passed (full suite)
```

## Verification Example
```bash
# Create test ticket with priority: 4
tf priority-reclassify --ids test-ticket --json
# Shows: "current": "P4", "proposed": "P1", "would_change": true

tf priority-reclassify --ids test-ticket --apply
# Updates priority to P1 and adds audit note
```

## Backward Compatibility
- Dry-run remains the default behavior
- All existing tests pass without modification
- `--apply` is an opt-in flag
