# Fixes: pt-n2dw

## Summary
Applied fixes for 2 Critical, 3 Major, and 4 Minor issues identified in code review.

## Critical Fixes

### 1. XSS Protection in `_render_markdown`
**File**: `tf_cli/web_ui.py`

**Issue**: Raw HTML in markdown could be executed via `{{ content_html|safe }}`.

**Fix**: Simplified the HTML escaping logic using Python's standard `html.escape()`:
```python
import html
content = html.escape(content)
return _md.convert(content)
```

This ensures `<script>` and other HTML tags are rendered as text, not executed.

### 2. Path Traversal Protection
**File**: `tf_cli/web_ui.py`

**Status**: Already implemented in original code at lines 318-321:
```python
doc_path = (knowledge_dir / doc.path).resolve()
if not str(doc_path).startswith(str(knowledge_dir.resolve())):
    return response.html("<h1>Access denied</h1>", status=403)
```

## Major Fixes

### 3. Case-Sensitive Document Type Validation
**File**: `tf_cli/web_ui.py`

**Status**: Already implemented - `doc_type = doc_type.lower()` on line 298.

### 4. Markdown Instance Recreation
**File**: `tf_cli/web_ui.py`

**Status**: Already implemented - Module-level `_md` instance used with `reset()`.

### 5. Silent Fail on IO Errors
**File**: `tf_cli/web_ui.py`

**Status**: Already implemented - Separate handling for `FileNotFoundError` vs `(IOError, OSError)`.

**Enhancement**: Added `read_error` to template context and display error message in UI.

## Minor Fixes

### 6. Duplicate `_find_repo_root` Function
**File**: `tf_cli/web_ui.py`

**Fix**: Removed local definition and import from `ui.py`:
```python
from tf_cli.ui import ..., _find_repo_root
```

### 7. Hardcoded Colors
**File**: `tf_cli/templates/doc_viewer.html`

**Fix**: Changed 3 occurrences of `#3498db` to `var(--brand-primary)`:
- `.back-link` color
- `.markdown-content a` color  
- `.markdown-content blockquote` border-left

### 8. Template Logic Duplication
**File**: `tf_cli/web_ui.py`, `tf_cli/templates/_doc_viewer.html`

**Fix**: 
- Route now passes `doc_type_info` list to template
- Template iterates over `doc_type_info` instead of hardcoded list
- `doc_availability` dict pre-computed to avoid template logic duplication

### 9. Jinja2 getattr Anti-pattern
**File**: `tf_cli/templates/_doc_viewer.html`

**Fix**: 
- Route pre-computes `doc_availability` dict
- Template uses `doc_availability.get(dt, false)` instead of `getattr(topic_obj, dt, None)`

## Files Changed
- `tf_cli/web_ui.py` - Import fix, XSS protection, route improvements
- `tf_cli/templates/_doc_viewer.html` - Use pre-computed data, error display
- `tf_cli/templates/doc_viewer.html` - CSS variable usage

## Verification
- ✓ Python syntax: `py_compile` passes
- ✓ Jinja2 templates: Compile and load successfully
- ✓ XSS protection: HTML entities are escaped
