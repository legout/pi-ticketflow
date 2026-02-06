# Review (Second Opinion): pt-6ztc

## Overall Assessment
The safety UX guardrails implementation is conceptually sound with good user-facing features (--yes, --max-changes, --force), but contains a critical logic bug where the `changes_to_make` list is filtered and capped but never used for actual application, causing confirmed changes to be silently skipped.

## Critical (must fix)
- `tf_cli/priority_reclassify_new.py:772-792` - The `changes_to_make` list is carefully constructed and capped by `--max-changes`, but the subsequent application loop at lines 812-830 iterates over `results` instead of `changes_to_make`, rendering the capping ineffective and potentially applying tickets in a different order than what was confirmed. **Fix**: Change the loop at line 812 to iterate over `changes_to_make` instead of `results`.

## Major (should fix)
- `tf_cli/priority_reclassify_new.py:785-791` - The `--max-changes` limit is applied AFTER interactive confirmation but BEFORE checking `--yes` flag. In non-interactive mode without `--yes`, the code exits with an error but the limit message was already printed, which could confuse users about what the actual error is. **Fix**: Move the max-changes capping inside the `if changes_to_make:` block after the confirmation check, or apply the limit at the time of confirmation and use the same list for application.
- `tf_cli/priority_reclassify_new.py:19-56` - `confirm_changes()` uses `max_changes` only for display but doesn't return a capped list. The caller must remember to apply the slice separately. This violates DRY and risks the confirmed set diverging from the applied set. **Fix**: Have `confirm_changes()` return the confirmed subset or apply the slice before confirmation.

## Minor (nice to fix)
- `tf_cli/priority_reclassify_new.py:774-779` - The force filtering logic uses `or args.force` which is always True when force is set. While functionally correct, it's confusing to read. **Fix**: Simplify to just check `if not args.force` and skip unknowns, or add a clarifying comment.
- `tf_cli/priority_reclassify_new.py:39` - The `confirm_changes()` display logic uses list slicing `changes[:max_changes]` which silently hides additional changes from the preview. A warning about omitted tickets would improve transparency.
- `tf_cli/priority_reclassify_new.py:14-15` - `is_interactive()` only checks stdin/stdout TTY status but not stderr. On some CI systems stderr might be a TTY while stdout is not, causing confusing behavior. Consider checking all three or documenting this limitation.

## Warnings (follow-up ticket)
- `tf_cli/priority_reclassify_new.py:812-830` - The update loop re-implements filtering logic (unknown check, max-changes check) that duplicates the pre-confirmation logic. This redundancy could drift in future changes. Consider refactoring to use a unified change application function.
- `tf_cli/priority_reclassify_new.py:19` - `confirm_changes()` accepts `List[dict]` with no type safety on the dict structure. A TypedDict or dataclass would prevent runtime errors from key mismatches.

## Suggestions (follow-up ticket)
- Add a `--dry-run` alias or make it the default (current default) more explicit in help text to prevent accidental discoveries
- Consider adding a `--select` flag to interactively pick which changes to apply from the list (like `git add -p`)
- Add rollback/undo support via the audit trail files - store old priority values so bulk changes can be reverted

## Positive Notes
- Good test coverage for the new safety features including edge cases for non-interactive mode
- The audit trail logging is well-implemented with clear markdown formatting
- The confirmation prompt displays a nicely formatted table with ticket details, making it easy for users to understand what will change
- JSON output mode is preserved and works correctly with the safety features
- KeyboardInterrupt handling in `confirm_changes()` provides clean cancellation without stack traces

## Summary Statistics
- Critical: 1
- Major: 2
- Minor: 3
- Warnings: 2
- Suggestions: 3
