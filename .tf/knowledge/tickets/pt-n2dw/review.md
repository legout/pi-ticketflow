# Review: pt-n2dw

## Critical (must fix)

- `tf_cli/web_ui.py` - **Path Traversal Vulnerability**: The `doc.path` value from index.json is used directly to construct a file path without validating that the resolved path stays within `knowledge_dir`. If index.json is compromised, arbitrary files could be read.
  **Fix**: Resolve and validate the path:
  ```python
  doc_path = (knowledge_dir / doc.path).resolve()
  if not str(doc_path).startswith(str(knowledge_dir.resolve())):
      return response.html("<h1>Access denied</h1>", status=403)
  ```

- `tf_cli/web_ui.py` + `tf_cli/templates/_doc_viewer.html` - **XSS Risk**: The `markdown` library renders raw HTML, and `{{ content_html|safe }}` bypasses Jinja2 autoescaping. Malicious markdown with `<script>` tags would execute.
  **Fix**: Sanitize HTML output using bleach or nh3, or strip raw HTML from markdown output.

## Major (should fix)

- `tf_cli/web_ui.py` - **Case-Sensitive Document Type Validation**: The `doc_type` validation is case-sensitive. Normalize to lowercase before validation.

- `tf_cli/web_ui.py` - **Markdown Instance Recreation**: Creating a new `Markdown` instance on every request is inefficient. Use a module-level instance with `reset()`.

- `tf_cli/web_ui.py` - **Silent Fail on IO Errors**: IO errors during file reading silently log to stderr and show "not found". Differentiate between missing files (expected) and read errors (500).

## Minor (nice to fix)

- `tf_cli/web_ui.py` - **Duplicate `_find_repo_root` Function**: Defined in both `web_ui.py` and `ui.py`. Import from `ui.py` instead.

- `tf_cli/templates/doc_viewer.html` - **Hardcoded Colors**: Uses `#3498db` instead of CSS variable `--brand-primary`.

- `tf_cli/templates/_doc_viewer.html` - **Template Logic Duplication**: Doc type list hardcoded in template and route. Pass from route to template.

- `tf_cli/templates/_doc_viewer.html` - **Jinja2 getattr Anti-pattern**: Using `getattr(topic_obj, dt, None)` is unidiomatic for dataclasses.

## Warnings (follow-up ticket)

- Add caching for Markdown rendering to avoid re-rendering large documents
- Consider `data-preserve-attr` for scroll position preservation during navigation
- Move inline CSS to separate files as the codebase grows
- Add document metadata (last modified, file size) to viewer

## Suggestions (follow-up ticket)

- Add document edit mode for future enhancement
- Add search within documents
- Add print stylesheet
- Add raw download endpoint for original markdown

## Summary Statistics
- Critical: 2
- Major: 3
- Minor: 4
- Warnings: 3
- Suggestions: 4

## Reviewers
- reviewer-general: Path traversal, XSS, case-sensitivity, error handling
- reviewer-spec-audit: All acceptance criteria met, 1 suggestion for scroll preservation
- reviewer-second-opinion: Path traversal, XSS, efficiency, error handling, code style
