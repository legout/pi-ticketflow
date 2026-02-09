# Implementation: pt-tupn

## Summary
Moved CLI dispatcher and core modules from `tf_cli` to `tf` namespace as a vertical slice migration. Updated all internal imports to prefer `tf.*` over `tf_cli.*`.

## Files Changed

### Core Modules Moved (with updated imports)
- `tf/utils.py` - Shared CLI utilities (find_project_root, read_json, merge)
- `tf/frontmatter.py` - Frontmatter manipulation utilities
- `tf/logger.py` - Ralph logging helper with redaction
- `tf/ticket_loader.py` - Ticket loading with lazy body loading
- `tf/component_classifier.py` - Component tag classification
- `tf/ticket_factory.py` - Ticket creation and backlog generation

### CLI Command Modules Moved
- `tf/agentsmd.py` - AGENTS.md management commands
- `tf/asset_planner.py` - Asset planning utilities
- `tf/backlog_ls.py` - Backlog listing commands
- `tf/board_classifier.py` - Board classification
- `tf/doctor.py` - Diagnostic commands
- `tf/hello.py` - Hello command
- `tf/init.py` - Project initialization
- `tf/kb_cli.py` - Knowledge base CLI
- `tf/kb_helpers.py` - Knowledge base helpers
- `tf/login.py` - Authentication commands
- `tf/new_cli.py` - New CLI namespace dispatcher
- `tf/next.py` - Next ticket command
- `tf/priority_reclassify.py` - Priority reclassification
- `tf/project_bundle.py` - Project bundling
- `tf/ralph.py` - Ralph loop management
- `tf/seed_cli.py` - Seed topic CLI
- `tf/session_store.py` - Session storage
- `tf/setup.py` - Setup wizard
- `tf/sync.py` - Model sync command
- `tf/tags_suggest.py` - Tag suggestion commands
- `tf/track.py` - File tracking command
- `tf/ui.py` - Interactive TUI
- `tf/update.py` - Update command

### Updated Files
- `tf/cli.py` - Updated all imports from `tf_cli.*` to `tf.*`
- `tf/new_cli.py` - Updated all imports from `tf_cli.*` to `tf.*`
- `tf/__init__.py` - Added ticket_factory exports

## Key Decisions
1. **Vertical Slice Approach**: Moved entire command modules at once rather than partial migrations
2. **Import Updates**: Changed all internal imports to use `tf.*` namespace
3. **Preserved tf_cli**: Original tf_cli package remains for backward compatibility
4. **No Breaking Changes**: Entry points already point to `tf.cli:main` (completed in pt-62g6)

## Testing
- All Python files compile successfully
- `python3 -m tf --help` works correctly
- `python3 -m tf --version` returns correct version
- `python3 -m tf new --help` works correctly
- All imports resolve without errors

## Migration Status
- tf/cli.py now imports from tf.* for all commands
- tf/new_cli.py imports from tf.* exclusively
- Core utilities now available in tf namespace
- Package structure ready for gradual tf_cli deprecation
