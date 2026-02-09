# Implementation: pt-n2dw

## Summary
Implemented inline document viewing for knowledge base documents in the web UI, replacing the terminal `$PAGER` approach with Datastar-powered inline rendering using Markdown with syntax highlighting.

## Files Changed

### 1. `pyproject.toml`
- Added `markdown>=3.5.0` dependency for Markdown rendering
- Added `pygments>=2.16.0` dependency for code syntax highlighting

### 2. `tf_cli/web_ui.py`
- Added imports for `markdown` library and extensions:
  - `FencedCodeExtension` - GitHub-style fenced code blocks
  - `TableExtension` - Markdown tables
  - `TocExtension` - Table of contents with heading IDs
  - `CodeHiliteExtension` - Syntax highlighting via Pygments
- Added `MD_EXTENSIONS` configuration for document rendering
- Added `_render_markdown(content)` helper function to render Markdown to HTML with syntax highlighting
- Added new route `/topic/<topic_id>/doc/<doc_type>` for inline document viewing:
  - Supports `overview`, `sources`, `plan`, `backlog` document types
  - Returns 400 for invalid document types
  - Returns 404 for missing topics or documents
  - Handles missing documents gracefully with "not found" message
  - Supports Datastar fragment requests for dynamic updates

### 3. `tf_cli/templates/_doc_viewer.html` (NEW)
- Fragment template for Datastar morphing
- Document tab navigation with Datastar `data-on:click` handlers
- Tab icons for each document type (📄 📚 📋 ✅)
- Active tab highlighting
- Disabled state for missing documents
- Document content rendering with fallback "not found" message

### 4. `tf_cli/templates/doc_viewer.html` (NEW)
- Full-page template extending `base.html`
- Complete styling for document viewer:
  - Document tabs with active/hover states
  - Markdown content styling (headings, lists, code, tables, blockquotes)
  - Pygments syntax highlighting colors (Dracula-inspired theme)
  - Responsive layout
- Back navigation link
- Topic header with type badge
- Includes `_doc_viewer.html` fragment

### 5. `tf_cli/templates/topic_detail.html`
- Made document items clickable with `data-on:click` for Datastar navigation
- Added hover effects on document items
- Added "View" button to document actions
- Documents now link to `/topic/<id>/doc/<type>` endpoint

## Key Decisions

1. **Datastar for Navigation**: Used `data-on:click="@get(...)"` for client-side navigation without page reloads, consistent with the existing board and topics UI.

2. **Fragment + Full Page Pattern**: Created both `_doc_viewer.html` (fragment) and `doc_viewer.html` (full page) to support both Datastar morphing and direct URL access.

3. **Markdown Extensions**: Selected extensions for rich document rendering:
   - `fenced_code` for code blocks
   - `tables` for data tables
   - `toc` for document structure
   - `codehilite` with Pygments for syntax highlighting

4. **Pygments Styling**: Added Dracula-inspired syntax highlighting colors inline to avoid external CSS dependencies.

5. **Graceful Degradation**: Missing documents show a friendly "not found" message instead of errors.

## Tests Run
- Verified markdown rendering with all extensions
- Verified syntax highlighting with Pygments
- Verified web_ui.py imports without errors
- Verified template syntax validity

## Verification
1. Start web UI: `tf ui --web`
2. Navigate to Topics → Select any topic with documents
3. Click on a document or the "View" button
4. Document renders inline with:
   - Markdown formatting
   - Syntax highlighting for code blocks
   - Navigation tabs for other documents
   - Proper styling matching the web UI theme

## Acceptance Criteria
- [x] Read and render markdown documents inline
- [x] Support syntax highlighting for code blocks
- [x] Handle missing documents gracefully (show "not found" message)
- [x] Support documents: overview.md, sources.md, plan.md, backlog.md
- [x] Add navigation between documents using `data-on:click`
- [x] Render document with styling consistent with web UI
