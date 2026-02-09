# Research: pt-m06z

## Status
Research complete. No external research needed - this is an internal refactoring task.

## Context Reviewed

### Ticket Requirements
- Update tests to import from `tf.*` where appropriate
- Add at least one test that imports `tf_cli` (shim) successfully
- CI passes
- Keep tests stable across Python versions >= 3.9

### Current State Analysis

#### Test Files Importing from `tf_cli`:
- `tests/test_next.py`: `from tf_cli import next`
- `tests/test_component_classifier.py`: `from tf_cli.component_classifier import ...`
- `tests/test_session_store.py`: `from tf_cli.session_store import ...`
- `tests/test_ralph_pi_invocation.py`: `from tf_cli import ralph as ralph_module`
- `tests/test_priority_reclassify.py`: `from tf_cli import priority_reclassify as pr`
- `tests/test_ralph_state.py`: `from tf_cli import ralph as ralph_module`
- `tests/test_kb_cli.py`: `from tf_cli.kb_cli import ...` and `from tf_cli.kb_helpers import ...`
- `tests/test_init.py`: `from tf_cli import init`
- `tests/test_ui_smoke.py`: Multiple imports from `tf_cli` and `tf_cli.cli`
- `tests/test_board_classifier.py`: `from tf_cli.board_classifier import ...` and `from tf_cli.ticket_loader import ...`

#### Test Files Already Using `tf`:
- `tests/test_cli_version.py`: `from tf.cli import main` (already migrated)

#### Package Structure:
- `tf/` - New canonical package with modules moved from `tf_cli/`
- `tf_cli/` - Deprecated shim that re-exports from `tf_cli` (some modules not yet moved)

#### Key Insight from Ralph Lessons (pt-tupn):
After moving modules between packages, always run comprehensive checks for remaining imports to the old namespace. The migration from `tf_cli` to `tf` requires updating test imports.

## Implementation Plan
1. Update test imports from `tf_cli.*` to `tf.*` for modules that exist in `tf/`
2. Keep `tf_cli` imports where modules haven't been moved yet (or verify they work through shim)
3. Add a dedicated regression test for `tf_cli` shim functionality
4. Run tests to verify everything passes

## Sources
- `tk show pt-m06z`
- `.tf/ralph/AGENTS.md` (lessons from pt-tupn)
- Direct codebase inspection
