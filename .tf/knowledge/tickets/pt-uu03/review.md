# Review: pt-uu03

## Critical (must fix)
- `.tf/knowledge/tickets/pt-uu03/implementation.md:1-50` - Implementation record claims "No files changed" and marks tests as failed, yet ticket is not blocked. Test collection failures must be resolved or explicitly accepted before any ticket can close. _(sources: reviewer-second-opinion)_
- `.tf/ralph/validation/pt-uu03-validation-log.md:11-14,113-117` - All required matrix scenarios are still unchecked/PENDING, so the primary deliverable (“execute and document manual validation scenarios”) was not completed. _(sources: reviewer-general)_
- `.tickets/pt-uu03.md:3,23-26,41` - Ticket is marked `status: closed` while every acceptance criterion remains unchecked and notes explicitly say required validation is still incomplete; this is a release/process-integrity failure. _(sources: reviewer-general)_
- `tests/test_post_fix_verification.py:10` - ImportError: cannot import name `_count_bullet_with_compound_fixes` from `tf.post_fix_verification`. The function was renamed to `_extract_fix_count_from_text` in the implementation but tests were not updated, causing test collection to fail. _(sources: reviewer-second-opinion)_
- `tests/test_post_fix_verification.py:10-84` - The test module still imports `_count_bullet_with_compound_fixes`, but `tf/post_fix_verification.py:149-174` only exposes `_extract_fix_count_from_text`; the mismatch causes `pytest -v` to abort (see `.tf/knowledge/tickets/pt-uu03/implementation.md:21-36`) and no test results are available for reviewers. _(sources: reviewer-spec-audit)_
- `tests/test_post_fix_verification.py:12` - The entire test class `TestCountBulletWithCompoundFixes` (lines 91-123) tests a non-existent function. All 4 test methods in this class will fail if the import issue is fixed, because they call `_count_bullet_with_compound_fixes` which doesn't exist. _(sources: reviewer-second-opinion)_
- `tests/test_post_fix_verification.py:14` and `tf/post_fix_verification.py:149` - Tests import `_count_bullet_with_compound_fixes`, but the module only defines `_extract_fix_count_from_text`; this causes pytest collection to fail and blocks validation. _(sources: reviewer-general)_
- `tickets/pt-uu03.md:22-26` - The ticket’s acceptance criteria (serial, parallel, fallback, timeout/orphan paths) and the plan’s acceptance block (`.tf/knowledge/topics/plan-ralph-background-interactive-shell/plan.md:111-120`) require documented scenarios, yet the validation matrix summary at `.tf/ralph/validation/pt-uu03-validation-log.md:9-118` still shows all tests as `PENDING` with no results, so none of the spec requirements have been satisfied. _(sources: reviewer-spec-audit)_

## Major (should fix)
- `.tf/knowledge/tickets/pt-uu03/implementation.md:10` - Claims "No files changed" but `.tf/ralph/validation/pt-uu03-validation-log.md` exists as a ticket-specific artifact created during this work. Implementation record is inconsistent. _(sources: reviewer-second-opinion)_
- `.tf/knowledge/tickets/pt-uu03/implementation.md:11` and `.tf/ralph/validation/pt-uu03-validation-log.md:1` - Implementation says “No files changed,” but a ticket-specific validation artifact exists; artifact tracking is inconsistent and weakens auditability. _(sources: reviewer-general)_
- `.tf/knowledge/tickets/pt-uu03/implementation.md:22-41` - Implementation records failed tests but still advances to review phase; unresolved test-collection failures need explicit triage/scope acceptance before sign-off. _(sources: reviewer-general)_
- `.tf/ralph/validation/pt-uu03-validation-log.md:14,34,52,69,105` - All 5 validation matrix checkboxes remain unchecked (PENDING). The core objective of this ticket was to "execute and document manual validation scenarios" but none were executed. _(sources: reviewer-second-opinion)_
- `.tf/ralph/validation/pt-uu03-validation-log.md:43-105` - Each test section is left with the `_To be filled during testing_` placeholder, so there is no recorded command/observation for serial, parallel, fallback, timeout, or orphan scenarios; without concrete steps and outcomes the manual validation matrix cannot be reproduced or audited. _(sources: reviewer-spec-audit)_
- `tests/test_post_fix_verification.py:263-265` - Test `test_parse_fixes_malformed_warning` expects warning message "no recognizable severity sections" but actual implementation returns "fixes.md found but no fix counts parsed" - assertion will fail. _(sources: reviewer-second-opinion)_
- `tf/post_fix_verification.py:86-95` - `_canonicalize_severity()` doesn't handle singular forms "warning" and "suggestion" which appear in test cases at `tests/test_post_fix_verification.py:33-34`. This is a latent bug that will surface once import issues are fixed. _(sources: reviewer-second-opinion)_

## Minor (nice to fix)
- `.tf/knowledge/tickets/pt-uu03/implementation.md:24-26` - Quality checks show all passing (lint, format, typecheck) but tests failed. The quality check logic should include test collection/import verification. _(sources: reviewer-second-opinion)_
- `.tf/knowledge/tickets/pt-uu03/implementation.md:4` - Summary content is formatted as an H1 heading under `## Summary`, which makes the artifact structure inconsistent. _(sources: reviewer-general)_
- `tf/post_fix_verification.py:101-124` - `_extract_fix_count_from_text()` has different semantics than the old function. It returns `int | None` and doesn't count bullets. The mismatch between test expectations and implementation suggests the refactor was incomplete. _(sources: reviewer-second-opinion)_
- `tf/post_fix_verification.py:129-147` - `_canonicalize_severity` only maps plural strings (`warnings`, `suggestions`) and falls back to `str.capitalize()`, so inputs like `warning`/`suggestion` return `Warning`/`Suggestion` instead of the canonical forms expected by `tests/test_post_fix_verification.py:44-48`; adding the singular mappings would make the helper match its own tests. _(sources: reviewer-spec-audit)_

## Warnings (follow-up ticket)
- `.tf/knowledge/tickets/pt-uu03/review.md:1` - Original review reports "Review failed: Review failed or output missing after /parallel run" - the review infrastructure itself may have issues requiring investigation. _(sources: reviewer-second-opinion)_
- `.tf/ralph/dispatch/pt-uu03.json` - Dispatch artifact likely has stale state (DISPATCHED) while progress marks COMPLETE. Stale state complicates recovery logic. _(sources: reviewer-second-opinion)_
- `.tf/ralph/dispatch/pt-uu03.json:8` vs `.tf/ralph/progress.md:319,325` - Dispatch state remains `DISPATCHED` while progress shows terminal states (`COMPLETE` and later `FAILED`), indicating stale/contradictory state tracking. _(sources: reviewer-general)_
- ``tf/ralph/dispatch/pt-uu03.json:1` - 9` vs `tf/ralph/progress.md:312-324` - The dispatch artifact still reports `status: DISPATCHED` while `progress.md` records the ticket as `COMPLETE` (and even `FAILED` later in the same file); this stale/inconsistent state makes it hard to trace which dispatch sessions actually completed and whether the validation matrix artifacts are tied to the same run. _(sources: reviewer-spec-audit)_
- `tests/test_post_fix_verification.py:1` - No CI check validates that test files are importable before merge. Consider adding `python -c "import tests.test_post_fix_verification"` to CI. _(sources: reviewer-second-opinion)_

## Suggestions (follow-up ticket)
- `.tf/ralph/validation/pt-uu03-validation-log.md:43-105` - Replace every `_To be filled during testing_` placeholder with the actual commands run, tool outputs, and observed results so future contributors can verify exactly what was exercised for each scenario. _(sources: reviewer-spec-audit)_
- `.tickets/pt-uu03.md:23-26` - Add an automated closure guard that blocks `status: closed` when acceptance checkboxes remain unchecked. _(sources: reviewer-general)_
- `Add validation matrix status check to ticket closure criteria` - prevent closing when acceptance criteria rows are PENDING. _(sources: reviewer-second-opinion)_
- `tests/test_post_fix_verification.py:14` - Add a lightweight CI import/collection smoke check (e.g., `pytest --collect-only` on critical test modules) to catch API/test drift earlier. _(sources: reviewer-general)_
- `unknown` - Add pre-commit hook to verify test file imports before allowing commit. _(sources: reviewer-second-opinion)_
- `unknown` - Consider mypy type checking in CI to catch function signature mismatches between tests and implementation. _(sources: reviewer-second-opinion)_
- `unknown` - Document expected behavior when a ticket has "No files changed" but creates artifacts in `.tf/ralph/validation/`. _(sources: reviewer-second-opinion)_

## Summary Statistics
- Critical: 8
- Major: 7
- Minor: 4
- Warnings: 5
- Suggestions: 7
