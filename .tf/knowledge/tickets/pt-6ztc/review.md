# Review: pt-6ztc

## Critical (must fix)
- `tf_cli/priority_reclassify_new.py:812-830` - The `changes_to_make` list is carefully constructed and capped by `--max-changes`, but the application loop iterates over `results` instead of `changes_to_make`, rendering the capping ineffective and potentially applying tickets in a different order than what was confirmed.

## Major (should fix)
- `tf_cli/priority_reclassify_new.py:785-791` - The `--max-changes` limit is applied AFTER interactive confirmation but BEFORE checking `--yes` flag. In non-interactive mode without `--yes`, the code exits with an error but the limit message was already printed.

## Minor (nice to fix)
- `tf_cli/priority_reclassify_new.py:774-779` - The force filtering logic uses `or args.force` which is always True when force is set. Simplify to just check `if not args.force`.
- `tf_cli/priority_reclassify_new.py:487-490` - Missing temp file cleanup on failure. Consider wrapping in try/except to unlink temp_path on failure.
- `tf_cli/priority_reclassify_new.py:657-660` - Max-changes limit in confirmation may differ from actual applied changes.

## Warnings (follow-up ticket)
- Consider refactoring to use a unified change application function to reduce duplication.
- `is_interactive()` only checks stdin/stdout TTY status but not stderr.

## Suggestions (follow-up ticket)
- Add `--dry-run` alias or make default more explicit in help text.
- Consider adding `--select` flag for interactive picking of changes.
- Add rollback/undo support via audit trail files.

## Summary Statistics
- Critical: 1
- Major: 1
- Minor: 3
- Warnings: 2
- Suggestions: 3
