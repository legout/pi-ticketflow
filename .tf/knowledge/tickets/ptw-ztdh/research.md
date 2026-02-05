# Research: ptw-ztdh

## Status
Research completed. No external research needed - this is an internal refactoring task.

## Context Reviewed

### Current Implementation

The codebase already has a shared component classifier module:

1. **`tf_cli/component_classifier.py`** - The shared module containing:
   - `DEFAULT_KEYWORD_MAP` - Keyword-to-component mapping
   - `classify_components()` - Core classification function
   - `suggest_tags_for_ticket()` - Fetch and classify a ticket
   - `format_tags_for_tk()` - Format tags for CLI use
   - `get_keyword_map_documentation()` - Generate docs

2. **`tf_cli/tags_suggest_new.py`** - Already uses the shared classifier:
   ```python
   from .component_classifier import (
       ClassificationResult,
       classify_components,
       format_tags_for_tk,
       get_keyword_map_documentation,
       suggest_tags_for_ticket,
   )
   ```

3. **`prompts/tf-backlog.md`** - References using the classifier for automatic tag assignment:
   ```python
   from tf_cli.component_classifier import classify_components, format_tags_for_tk
   
   result = classify_components(title, description)
   component_tags = result.tags
   ```

### Findings

- The shared classifier logic is ALREADY in place in `component_classifier.py`
- `tags_suggest_new.py` already imports and uses it
- The `/tf-backlog` prompt documents using the same classifier

### What Needs to Be Done

1. Add module-level documentation to `component_classifier.py` explaining it's the shared source of truth
2. Update `docs/commands.md` to document the relationship between `/tf-backlog` and `/tf-tags-suggest`
3. Update the `prompts/tf-backlog.md` to reference the shared module explicitly

## Sources
- `tf_cli/component_classifier.py` - Shared classifier module
- `tf_cli/tags_suggest_new.py` - Consumer of the classifier
- `prompts/tf-backlog.md` - Backlog command prompt
- `docs/commands.md` - Command documentation
