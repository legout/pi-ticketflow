# Implementation: pt-j2it

## Summary
Updated `docs/ralph-logging.md` to enhance troubleshooting section with artifact path pointers and clarify default log output destination.

## Files Changed
- `docs/ralph-logging.md` - Enhanced documentation

## Key Changes

### 1. Quick Start Section
Added clarification that **logs go to stderr** (not stdout) to avoid mixing with data pipes.

### 2. New "Where to look after failures" Troubleshooting Section
Added comprehensive guide covering:
- Artifact directory structure: `.tf/knowledge/tickets/<ticket-id>/`
- File-by-file breakdown of what each artifact contains
- Example error log showing artifact_path field
- Quick inspection commands

### 3. New "Session traces (experimental)" Section
Documented the JSONL session capture feature:
- Location: `.tf/ralph/sessions/<ticket-id>.jsonl`
- Format: JSON lines (structured events)
- Status: Experimental feature

## Acceptance Criteria Verification

| Criteria | Status | Implementation |
|----------|--------|----------------|
| Default log output documented | ✅ | Added "Output goes to stderr" to Quick Start |
| Verbose/debug enablement documented | ✅ | Already existed (env vars + flags) |
| Troubleshooting section includes artifact pointers | ✅ | New "Where to look after failures" section |
| `.tf/ralph/progress.md` mentioned | ✅ | Already in "Loop stops early" section |
| `.tf/knowledge/tickets/<id>/` documented | ✅ | New section with file-by-file breakdown |
| JSON capture documented (if exists) | ✅ | New "Session traces (experimental)" section |

## Tests Run
- Verified markdown formatting
- Checked all internal links work

## Verification

```bash
# View updated documentation
cat docs/ralph-logging.md

# Verify artifact paths exist
ls .tf/knowledge/tickets/pt-l6yb/  # Example completed ticket
```

## Notes
- Documentation was already comprehensive; changes are incremental improvements
- JSON capture is marked as experimental since pt-uo6h is still open
- Kept docs short and concrete as per constraints
