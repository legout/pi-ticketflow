# Fixes: pt-tupn

## Summary
Fixed all Critical and Major issues identified in review, plus Minor documentation issues. Verified no remaining `tf_cli` imports in the `tf/` package.

## Fixes Applied

### Critical (must fix)
1. **`tf/board_classifier.py:20`** - Updated import from `tf_cli.ticket_loader` to `tf.ticket_loader`
2. **`tf/board_classifier.py:364`** - Fixed docstring example to reference `tf.ticket_loader` instead of `tf_cli.ticket_loader`

### Major (should fix)
3. **`tf/asset_planner.py:118`** - Changed repo detection fallback from `(parent / "tf_cli").is_dir()` to `(parent / "tf").is_dir()`
4. **`tf/cli.py:57`** - Changed repo detection fallback from `(parent / "tf_cli").is_dir()` to `(parent / "tf").is_dir()`

### Minor (nice to fix)
5. **`tf/__init__.py:102-107`** - Added `TicketDef`, `CreatedTicket`, `create_tickets`, `score_tickets` to `__all__`
6. **`tf/tags_suggest.py:4`** - Updated docstring to reference `tf.component_classifier` instead of `tf_cli.component_classifier`

## Verification
- All Python files compile successfully
- `python3 -c "from tf.board_classifier import BoardClassifier; from tf.ticket_loader import TicketLoader"` works
- `python3 -m tf --version` returns correct version (0.3.0)
- `python3 -m tf --help` shows all commands
- `grep -r "from tf_cli" tf/` returns no results

## Tests
- Smoke tests pass: imports, version, help commands
- No remaining tf_cli imports in tf/ package

## Files Changed
- tf/board_classifier.py
- tf/asset_planner.py
- tf/cli.py
- tf/__init__.py
- tf/tags_suggest.py
