# Fixes: pt-6ztc

## Critical Issue Fixed

### Problem
The `changes_to_make` list was carefully constructed and capped by `--max-changes`, but the application loop iterated over the full `results` list instead of `changes_to_make`. This caused:
1. The `--max-changes` capping to be ineffective
2. Tickets potentially being applied in a different order than what was confirmed
3. Unknown priorities being applied even without `--force`

### Fix
Changed the apply loop to iterate over `changes_to_make` instead of `results`:
- Removed redundant filtering logic from the apply loop
- The `changes_to_make` list now correctly reflects exactly what will be applied
- Simplified the force flag logic for clarity

## Minor Improvements

1. **Simplified force flag logic** (lines 774-779):
   - Before: Complex conditional with `or args.force`
   - After: Simple `if not args.force` check

2. **Removed dead code**:
   - Removed `skipped_count` tracking that was no longer needed
   - Removed redundant filtering in apply loop

## Files Changed
- `tf_cli/priority_reclassify_new.py`
