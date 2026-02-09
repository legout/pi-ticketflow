# Review (Spec Audit): pt-tupn

## Overall Assessment
The migration made substantial progress: CLI dispatch now exists in `tf/cli.py`, and many modules were copied into `tf/`. However, the ticket is not fully spec-compliant yet. Two acceptance criteria remain unmet: internal imports are not consistently `tf.*`, and the test suite is currently failing.

## Critical (must fix)
- `tests/test_cli_version.py:31,42,53,63,77,86,95,107,117` + `tf/__init__.py:91-96` - **"All tests pass" acceptance criterion is not met.** Running `pytest -q tests/test_cli_version.py` currently fails 9 tests. Since ticket AC explicitly requires all tests to pass, this is a blocking compliance gap.
- `tf/board_classifier.py:20` - Imports `Ticket`/`TicketLoader` from `tf_cli.ticket_loader` instead of `tf.ticket_loader`. This violates the ticket requirement to update internal imports to prefer `tf.*`.

## Major (should fix)
- `tf/cli.py:57` - Repo-root fallback still checks for `(parent / "tf_cli").is_dir()` instead of `tf`. This keeps core CLI wiring coupled to the legacy namespace and conflicts with the migration intent.
- `tf/asset_planner.py:118` - Same legacy fallback check for `tf_cli` directory. This is another remaining internal dependency on old namespace conventions.

## Minor (nice to fix)
- `tf/tags_suggest.py:4` - Module docstring still states shared classifier lives under `tf_cli.component_classifier`, which is outdated after migration and can confuse future maintainers.

## Warnings (follow-up ticket)
- `tf/board_classifier.py:364` - Example code in docstring still references `tf_cli.ticket_loader`. Not functionally blocking, but it can propagate old namespace usage in docs/examples.

## Suggestions (follow-up ticket)
- `tests/` (new test suggested) - Add a regression check that production modules under `tf/` do not import `tf_cli.*` (except explicitly allowed compatibility shim modules), to prevent namespace backsliding during incremental moves.

## Positive Notes
- `tf/cli.py` is now the canonical dispatcher and routes commands through `tf.*` modules.
- `tf_cli/cli.py` is converted to a compatibility shim delegating to `tf.cli`, consistent with the broader migration strategy.
- A large vertical slice of modules has been moved under `tf/`, matching the incremental migration constraint.

## Summary Statistics
- Critical: 2
- Major: 2
- Minor: 1
- Warnings: 1
- Suggestions: 1

## Spec Coverage
- Spec/plan sources consulted: `tk show pt-tupn`, `.tickets/pt-tupn.md`, `.tf/knowledge/tickets/pt-tupn/implementation.md`, `.tf/knowledge/topics/plan-refactor-tf-cli-to-tf/plan.md`, `.tf/knowledge/topics/plan-refactor-tf-cli-to-tf/backlog.md`, `.tf/knowledge/topics/plan-refactor-tf-cli-to-tf/sources.md`
- Missing specs: none
