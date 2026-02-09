# Review: pt-tupn

## Overall Assessment
The migration is largely successful with 32 Python modules now in the `tf/` namespace. However, several files still contain `tf_cli` imports that need to be updated to complete the migration goal of preferring `tf.*` imports.

## Critical (must fix)
- `tf/board_classifier.py:20` - Import statement uses `from tf_cli.ticket_loader import Ticket, TicketLoader` instead of `from tf.ticket_loader import Ticket, TicketLoader`. This defeats the migration's stated goal to have all modules in `tf/` import from `tf.*` namespace.
- `tf/board_classifier.py:364` - Docstring example still references `>>> from tf_cli.ticket_loader import TicketLoader` instead of the updated `>>> from tf.ticket_loader import TicketLoader`.

## Major (should fix)
- `tf/asset_planner.py:118` - Repo-root fallback detection requires `(parent / "tf_cli").is_dir()`. When `tf_cli` is eventually removed, local/offline repo detection may fail.
- `tf/cli.py:57` - Same `tf_cli`-directory fallback assumption in `resolve_repo_root()`. Creates future breakage in CLI root resolution during deprecation cleanup.

## Minor (nice to fix)
- `tf/__init__.py:99-105` - Ticket factory symbols are imported (`TicketDef`, `CreatedTicket`, `create_tickets`, `score_tickets`) but not included in `__all__`. This makes the "added ticket_factory exports" change incomplete for wildcard/public API expectations.
- `tf/tags_suggest.py:4` - Module docstring still says shared source is `tf_cli.component_classifier`; implementation now uses `tf.component_classifier`.

## Warnings (follow-up ticket)
- `tests/` (multiple files) - Test suite coverage is still heavily centered on `tf_cli.*` imports. Add/shift tests to assert `tf.*` namespace behavior directly, so future deprecation of `tf_cli` is safer.

## Suggestions (follow-up ticket)
- `tf/cli.py`, `tf/asset_planner.py` - Centralize repo-root detection in one helper to avoid duplicated fallback logic drifting across modules.
- Consider adding a verification step that searches for remaining `from tf_cli` imports in the `tf/` package to catch issues earlier.

## Positive Notes
- `tf/cli.py` and `tf/new_cli.py` dispatch now consistently route to `tf.*` modules for command execution.
- Migration kept backward compatibility by preserving `tf_cli` while moving substantial vertical slices into `tf`.
- Smoke checks (`python3 -m tf --version`, `--help`, `new --help`) execute successfully.
- Core utilities properly migrated: `utils.py`, `frontmatter.py`, `logger.py`, `ticket_loader.py`, `component_classifier.py`, `ticket_factory.py`.

## Summary Statistics
- Critical: 2
- Major: 2
- Minor: 2
- Warnings: 1
- Suggestions: 2

## Review Sources
- reviewer-general: Major issues with tf_cli fallback detection
- reviewer-second-opinion: Critical board_classifier.py import issues
