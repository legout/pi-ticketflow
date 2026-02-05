# Implementation: ptw-ztdh

## Summary
Updated documentation to clarify that `/tf-backlog` and `/tf-tags-suggest` share the same component classifier logic from `tf_cli.component_classifier`. No code changes were needed as the shared module was already in place.

## Files Changed
- `tf_cli/component_classifier.py` - Added module-level documentation explaining it's the shared source of truth
- `tf_cli/tags_suggest_new.py` - Updated module docstring to reference the shared classifier
- `docs/commands.md` - Added documentation about the shared classifier relationship in both `/tf-backlog` and `/tf-tags-suggest` sections
- `prompts/tf-backlog.md` - Updated to explicitly mention the shared classifier module

## Key Decisions
- **No code refactoring needed**: The shared classifier module (`component_classifier.py`) already existed and was being used by `tags_suggest_new.py`. The `/tf-backlog` prompt already referenced using it.
- **Documentation-only changes**: The primary work was clarifying the relationship between the commands through improved documentation.
- **Maintained backwards compatibility**: All existing tests pass without modification.

## Implementation Details

### 1. component_classifier.py
Added comprehensive module docstring explaining:
- This is the shared source of truth for component classification
- Both `/tf-backlog` and `/tf-tags-suggest` use this module
- Usage patterns for each consumer

### 2. tags_suggest_new.py
Updated module docstring to:
- Reference the shared classifier module
- Explain the relationship with `/tf-backlog`
- List the CLI commands provided

### 3. docs/commands.md
Added documentation in two places:
- `/tf-backlog` section: Added "Component Tag Assignment" subsection explaining automatic tagging uses the shared classifier
- `/tf-tags-suggest` section: Added "Shared Classifier" subsection explaining it uses the same module as `/tf-backlog`

### 4. prompts/tf-backlog.md
Updated step 8 to:
- Explicitly mention the shared classifier
- Note it's the same module used by `/tf-tags-suggest`

## Tests Run
```bash
pytest tests/test_component_classifier.py -v
```
Result: **24 passed** - All existing tests pass, confirming backwards compatibility.

## Verification
- [x] Module docstrings updated
- [x] Command documentation updated
- [x] Prompt documentation updated
- [x] All tests pass
- [x] Files tracked for commit

## Relationship Summary
```
                     tf_cli.component_classifier
                              (shared)
                                 |
            +--------------------+--------------------+
            |                                         |
    /tf-backlog (prompt)                    /tf-tags-suggest (CLI)
    - Automatic during                      - Explicit fallback
      ticket creation                         command
    - Uses classify_components()            - Uses same classify_components()
```

Both paths now explicitly document that they share the same classification logic, ensuring consistent `component:*` tag suggestions across the ticketflow system.
