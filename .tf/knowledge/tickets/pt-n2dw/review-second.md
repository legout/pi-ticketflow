# Review (Second Opinion): pt-n2dw

## Overall Assessment
The implementation successfully adds inline document viewing with Datastar integration, but introduces several security concerns that must be addressed before merge. The code is generally well-structured following existing patterns, but lacks proper input sanitization and HTML safety measures when rendering untrusted markdown content.

## Critical (must fix)

- `tf_cli/web_ui.py:282` - **Path Traversal Vulnerability**: The `doc.path` value from index.json is used directly to construct a file path without validation. If index.json contains a malicious entry like `"overview": "../../../etc/passwd"`, the system will read arbitrary files. **Fix**: Validate that the resolved path is within the knowledge directory:
  ```python
  doc_path = knowledge_dir / doc.path
  doc_path = doc_path.resolve()
  if not str(doc_path).startswith(str(knowledge_dir.resolve())):
      return response.html("Invalid document path", status=400)
  ```

- `tf_cli/web_ui.py:54-60` + `tf_cli/templates/_doc_viewer.html:37` - **XSS via Markdown HTML**: The `markdown` library with default settings does NOT sanitize HTML. Malicious markdown containing `<script>alert('xss')</script>` will be rendered and executed when piped through `|safe`. **Fix**: Either enable `safe_mode` (deprecated) or use `bleach`/`nh3` to sanitize the HTML output, or use a markdown extension like `markdown.extensions.codehilite` with `use_pygments=True` but also strip raw HTML:
  ```python
  import bleach
  allowed_tags = ['p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'code', 'pre', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'blockquote', 'strong', 'em', 'a']
  allowed_attrs = {'a': ['href'], 'code': ['class'], 'pre': ['class']}
  content_html = bleach.clean(md.convert(content), tags=allowed_tags, attributes=allowed_attrs)
  ```

## Major (should fix)

- `tf_cli/web_ui.py:48-55` - **Markdown Instance Recreation**: Creating a new `Markdown` instance on every request in `_render_markdown()` is inefficient. The `Markdown` class is designed to be reusable. **Fix**: Create a module-level instance or use `functools.lru_cache`:
  ```python
  _md = markdown.Markdown(extensions=MD_EXTENSIONS)
  
  def _render_markdown(content: str) -> str:
      _md.reset()
      return _md.convert(content)
  ```

- `tf_cli/web_ui.py:296-297` - **Silent Fail on IO Errors**: When a document fails to read due to permissions or other IO errors, the code silently logs to stderr and shows "Document not found" to the user. This masks actual problems and provides poor UX. **Fix**: Differentiate between "file doesn't exist" (expected) and "cannot read file" (error). Return 500 for actual errors.

## Minor (nice to fix)

- `tf_cli/templates/doc_viewer.html:125` - **Hardcoded Colors**: Uses hardcoded color `#3498db` instead of CSS variable `--brand-primary` used elsewhere in the stylesheet. This breaks theming consistency. Same issue on lines 151, 181 with colors `#2d3748`, `#95a5a6`.

- `tf_cli/templates/_doc_viewer.html:8` - **Template Logic Duplication**: The doc type list `['overview', 'sources', 'plan', 'backlog']` is hardcoded in both the template and the route handler (`valid_doc_types`). This creates maintenance burden if new doc types are added. **Fix**: Pass the list to the template from the route.

- `tf_cli/templates/_doc_viewer.html:8` - **Jinja2 getattr Anti-pattern**: Using `getattr(topic_obj, dt, None)` in templates is unidiomatic. Since `Topic` is a dataclass, use `topic_obj[dt]` or pass a pre-computed dict instead.

- `tf_cli/templates/topic_detail.html:115` - **Unused Topic_obj Access**: The template accesses `topic_obj[doc_type]` which will fail if `topic_obj` is None (defensive coding issue).

## Warnings (follow-up ticket)

- `tf_cli/web_ui.py:220-224` - **No Fragment Caching**: Document content is re-rendered from markdown on every request. For large documents, this is expensive. Consider adding a simple cache (TTL or file mtime-based).

- `tf_cli/templates/doc_viewer.html:1-225` - **Inline Stylesheet Size**: The template embeds ~225 lines of CSS. As more pages are added, this approach will bloat page sizes. **Suggestion**: Move page-specific CSS to separate files and include conditionally, or use a CSS build process.

## Suggestions (follow-up ticket)

- `pyproject.toml:16-17` - **Missing Bleach Dependency**: If HTML sanitization is added (recommended in Critical section), add `bleach>=6.0.0` or `nh3` to dependencies.

- `tf_cli/web_ui.py:207-224` - **Missing Document Metadata**: The document viewer doesn't show file metadata (last modified, file size). Useful for users to know if content is stale.

- `tf_cli/web_ui.py` - **Add Document Export**: Consider adding a raw download endpoint (`/topic/<id>/doc/<type>/raw`) to download the original markdown file.

## Positive Notes

- Clean separation of fragment (`_doc_viewer.html`) and full page (`doc_viewer.html`) templates following established patterns in the codebase.
- Good use of Datastar for client-side navigation without full page reloads, consistent with the existing board UI.
- Proper HTTP status codes (400 for invalid doc_type, 404 for missing topics/documents).
- The `autoescape=True` setting on Jinja2 Environment is correctly set for security (though bypassed by `|safe`).
- Nice touch with document type icons and disabled state for missing documents.

## Summary Statistics
- Critical: 2
- Major: 2
- Minor: 4
- Warnings: 2
- Suggestions: 3
