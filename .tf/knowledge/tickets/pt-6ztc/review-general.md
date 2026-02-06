# Review: pt-6ztc

## Overall Assessment
The implementation successfully adds safety UX guardrails to the priority reclassify command. All acceptance criteria are met: `--apply` requires `--yes` in non-interactive mode, `--max-changes` caps updates, and `--force` allows applying unknown classifications. The code is well-structured with 36 passing tests covering the new functionality. Minor issues exist around temp file cleanup consistency and a redundant conditional in the force flag logic.

## Critical (must fix)
No issues found.

## Major (should fix)
No issues found.

## Minor (nice to fix)
- `tf_cli/priority_reclassify_new.py:530-532` - Redundant conditional in force flag filtering. The expression `r["proposed"] != "unknown" or args.force` always evaluates to `True` when `args.force` is `True`, making the filter ineffective when force is enabled. Simplify to: `if not args.force: changes_to_make = [r for r in changes_to_make if r["proposed"] != "unknown"]`

- `tf_cli/priority_reclassify_new.py:487-490` - Missing temp file cleanup on failure. Unlike `session_store.py` which uses try/except/finally to clean up temp files, this code leaves `.md.tmp` files if an exception occurs between `write_text()` and `replace()`. Consider wrapping in try/except to unlink temp_path on failure.

- `tf_cli/priority_reclassify_new.py:657-660` - Max-changes limit in confirmation may differ from actual applied changes. The `changes_to_make` list is sliced for confirmation display, but the actual apply loop iterates over full `results` with a counter check. This could lead to discrepancy if the results order differs from changes_to_make order. Consider using the same filtered list for both confirmation and application.

- `tf_cli/priority_reclassify_new.py:672` - Audit trail doesn't reflect max_changes limit. The `write_audit_trail()` call uses full `results` list, not accounting for tickets that weren't applied due to max_changes cap. The "Applied" column may show "Yes" for tickets that weren't actually applied.

## Warnings (follow-up ticket)
- `tf_cli/priority_reclassify_new.py:13-14` - The `is_interactive()` helper only checks stdin/stdout but not stderr. Some CI environments may have stdout as TTY but not stdin. Consider checking all three standard streams for robustness.

- `tf_cli/priority_reclassify_new.py:29-47` - `confirm_changes()` doesn't handle case where max_changes is less than actual changes. The message says "only first N will be applied" but doesn't show which tickets are being excluded, which could confuse users.

## Suggestions (follow-up ticket)
- `tf_cli/priority_reclassify_new.py:477` - Consider preserving file permissions when updating tickets. The atomic write creates a new file which may have different permissions than the original. Use `shutil.copymode()` or `os.chmod()` after replace.

- `tf_cli/priority_reclassify_new.py:500-511` - The note timestamp format uses local time but appends 'Z' suffix suggesting UTC. Consider using explicit UTC: `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`

- Add dry-run output that shows exactly which tickets would be affected by max_changes before confirmation, to help users understand the scope of changes.

## Positive Notes
- Comprehensive test coverage with 36 tests, all passing
- Good separation of concerns with dedicated helpers (`is_interactive()`, `confirm_changes()`)
- Clean handling of both TTY and non-TTY modes with clear error messages
- Proper atomic file write pattern using temp file + replace (though missing cleanup)
- Well-structured argument parsing with clear help text for new flags
- Good backward compatibility - existing behavior preserved when new flags not used

## Summary Statistics
- Critical: 0
- Major: 0
- Minor: 4
- Warnings: 2
- Suggestions: 3
