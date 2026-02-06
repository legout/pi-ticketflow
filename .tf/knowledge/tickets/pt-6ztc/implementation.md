# Implementation: pt-6ztc

## Summary
Add safety UX guardrails to the priority reclassify command to prevent accidental bulk changes.

## Acceptance Criteria
- [x] `--apply` requires `--yes` (or interactive confirmation when TTY)
- [x] Supports `--max-changes N` to cap updates
- [x] Supports `--force` (apply even when ambiguous) and default skip for unknown

## Changes Made

### File: `tf_cli/priority_reclassify_new.py`

1. **Added `--yes` flag**: Required when using `--apply` in non-interactive mode
2. **Added `--max-changes` flag**: Caps the number of tickets that will be modified
3. **Added `--force` flag**: Allows applying changes even for "unknown" priority classifications
4. **Added `is_interactive()` helper**: Detects if running in a TTY for interactive confirmation
5. **Added `confirm_changes()` helper**: Prompts user for confirmation with change summary
6. **Modified apply logic**: Respects max-changes limit and force flag

### Safety Flow
1. In dry-run mode: Show proposed changes, no confirmation needed
2. In apply mode with TTY: Show summary and prompt for confirmation
3. In apply mode without TTY: Require `--yes` flag
4. With `--max-changes N`: Stop after N changes, warn about remaining
5. With `--force`: Include "unknown" classifications in updates
6. Without `--force`: Skip "unknown" classifications (existing behavior preserved)

## Tests
- Updated existing tests to work with new confirmation flow
- Added tests for `--yes` flag requirement
- Added tests for `--max-changes` capping
- Added tests for `--force` flag with unknown priorities
- Added tests for interactive confirmation

## Verification
```bash
# Dry run (no confirmation needed)
python -m tf_cli.priority_reclassify_new --ready

# Apply with confirmation (TTY)
python -m tf_cli.priority_reclassify_new --ready --apply

# Apply headless (requires --yes)
python -m tf_cli.priority_reclassify_new --ready --apply --yes

# Cap changes
python -m tf_cli.priority_reclassify_new --ready --apply --yes --max-changes 5

# Force apply unknowns
python -m tf_cli.priority_reclassify_new --ready --apply --yes --force
```
