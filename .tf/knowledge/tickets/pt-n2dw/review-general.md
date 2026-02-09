# Review: pt-n2dw

## Overall Assessment
Good implementation of inline document viewing for the knowledge base. The code follows existing patterns in the codebase, uses Datastar consistently for client-side navigation, and provides both fragment and full-page rendering. The Markdown rendering with syntax highlighting is well-integrated. However, there are some security concerns around path traversal and XSS that need addressing.

## Critical (must fix)
- `tf_cli/web_ui.py:341-347` - **Path Traversal Vulnerability**: The `topic_document` route constructs file paths using `knowledge_dir / doc.path` without validating that the resolved path stays within `knowledge_dir`. If `index.json` is compromised or manipulated, arbitrary files could be read. Fix by resolving the path and checking it starts with `knowledge_dir`:
  ```python
  doc_path = knowledge_dir / doc.path
  doc_path = doc_path.resolve()
  if not str(doc_path).startswith(str(knowledge_dir.resolve())):
      return response.html("<h1>Access denied</h1>", status=403)
  ```

- `tf_cli/templates/_doc_viewer.html:34` - **XSS Risk with `|safe` Filter**: Using `{{ content_html|safe }}` renders raw HTML without escaping. While markdown content comes from trusted files, a compromised knowledge base file could inject malicious scripts. Consider sanitizing the HTML or adding a Content Security Policy header. At minimum, document this trust assumption.

## Major (should fix)
- `tf_cli/web_ui.py:330-333` - **Case-Sensitive Document Type Validation**: The `doc_type` validation is case-sensitive (`overview` vs `OVERVIEW`). This could lead to 400 errors for mixed-case URLs. Consider normalizing to lowercase: `doc_type = doc_type.lower()` before validation.

- `tf_cli/web_ui.py:336-337` - **Missing Error Detail on Topic Load Failure**: If `loader.load()` fails (e.g., corrupt index.json), the exception propagates to the generic 500 handler without useful context. Consider catching `TopicIndexLoadError` separately and returning a more informative error message.

- `tf_cli/templates/topic_detail.html:79` - **Inconsistent `getattr` Usage**: The template uses `getattr(topic_obj, doc_type, None)` but this relies on Jinja2's built-in `getattr` which may not handle all edge cases consistently. Consider passing a pre-computed doc availability map from the view instead of using `getattr` in templates.

## Minor (nice to fix)
- `tf_cli/web_ui.py:20-25` - **Inconsistent Import Style**: The markdown extensions are imported with full paths while other imports use simpler forms. Not a bug, but inconsistent with the rest of the file's style.

- `tf_cli/templates/doc_viewer.html:145-168` - **Hardcoded Pygments Theme**: The Dracula-inspired colors are hardcoded inline. Consider extracting to a CSS variable scheme or documenting how to customize.

- `tf_cli/web_ui.py:49-55` - **Duplicate `_find_repo_root` Function**: This function is defined both in `web_ui.py` and `ui.py`. Consider importing from `ui.py` to avoid code duplication.

- `tf_cli/web_ui.py:324-325` - **Fragment Detection Comment**: The comment says "has target header or fragment param" but the code checks `datastar-request` header (not "target"). Minor documentation inconsistency.

## Warnings (follow-up ticket)
- `tf_cli/web_ui.py:341` - **File Handle Not Closed on Exception**: While the `with` statement handles normal cases, if an exception occurs during `f.read()`, the traceback might be less clear. This is handled by the outer try/except, but consider using `Path.read_text()` for simplicity.

- `tf_cli/templates/_doc_viewer.html:12-22` - **Repeated Icon Logic**: The emoji icon mapping is duplicated in both `_doc_viewer.html` and `topic_detail.html`. Consider creating a Jinja2 macro or passing icon mapping from the view.

- `pyproject.toml` - **No Version Constraints File**: New dependencies (`markdown`, `pygments`) are added with `>=` constraints. Consider pinning to major versions to avoid breaking changes: `markdown>=3.5.0,<4.0.0`.

## Suggestions (follow-up ticket)
- **Add Caching for Markdown Rendering**: Large documents could be expensive to render on every request. Consider caching rendered HTML in memory with a simple TTL cache.

- **Add Document Edit Mode**: The viewer is read-only. A future enhancement could add an edit button that opens the raw markdown in a text editor or provides inline editing.

- **Add Search Within Documents**: The Markdown content could be indexed for full-text search across all knowledge base documents.

- **Add Print Stylesheet**: The document viewer looks good on screen but could benefit from print-specific CSS for generating PDFs.

## Positive Notes
- Good use of the fragment + full page pattern for Datastar compatibility
- Consistent styling with the existing web UI theme using CSS variables
- Proper handling of missing documents with friendly "not found" messages
- Clean separation of concerns: `_render_markdown` helper is well-isolated
- Good use of Jinja2 `autoescape=True` for security (though `|safe` bypasses it)
- The Datastar navigation with `data-on:click` is consistent with other parts of the UI
- Tab-based navigation between document types is intuitive

## Summary Statistics
- Critical: 2
- Major: 3
- Minor: 4
- Warnings: 3
- Suggestions: 4
