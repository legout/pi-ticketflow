# Research: pt-tupn

## Task
Move CLI dispatcher + core modules from tf_cli to tf namespace.

## Current State Analysis

### Entrypoints (already correct)
- `pyproject.toml` has `tf = "tf.cli:main"` ✓
- `tf/__main__.py` already imports from `tf.cli` ✓
- `tf_cli/__main__.py` already delegates to `tf.cli` ✓

### tf/ package (minimal)
- `tf/__init__.py` - version handling, docstring notes migration
- `tf/cli.py` - CLI dispatcher with imports from `tf_cli.*`
- `tf/__main__.py` - module entrypoint

### tf_cli/ package (full implementation)
Contains 30+ modules including:
- Core CLI: `cli.py`, `new_cli.py`
- Commands: `setup.py`, `login.py`, `init.py`, `sync.py`, `doctor.py`, etc.
- Utilities: `version.py`, `utils.py`, `frontmatter.py`, `ticket_factory.py`

## Migration Strategy

Vertical slice approach - move essential modules first:
1. `new_cli.py` - core command dispatcher
2. `setup.py` - setup command
3. `login.py` - login command

Then update `tf/cli.py` imports to use `tf.*` instead of `tf_cli.*` for moved modules.

## Acceptance Criteria
- [ ] CLI dispatch code lives under `tf/`
- [ ] Internal imports updated (prefer `tf.*`)
- [ ] All tests pass

## References
- Ticket pt-62g6 already closed (entrypoints wired)
- Lesson from pt-hpme: maintain behavioral parity when moving code
