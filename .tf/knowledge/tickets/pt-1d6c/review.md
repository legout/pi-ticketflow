# Review: pt-1d6c

## Critical (must fix)

- `tf_cli/web_ui.py:52-54` - **Empty board misclassified as error**: The `if not board_view:` check treats an empty `BoardView` (valid state with 0 tickets) as an error. `BoardView` with empty `all_tickets` list is falsy, causing 500 errors for new/empty projects. Should check `if board_view is None:` instead. *(from reviewer-general)*

- `tf_cli/web_ui.py:33` - **Jinja2 autoescaping disabled, creating XSS vulnerability**: The `Environment` is created without `select_autoescape()` or `autoescape=True`. Combined with `ticket.html:102` rendering `{{ ticket.body }}` directly, this allows stored XSS attacks if ticket content contains malicious scripts. *(from reviewer-second-opinion)*

- `tf_cli/templates/_board.html:1` + `tf_cli/templates/index.html:137` - **Structural mismatch breaks Datastar morphing**: The `_board.html` fragment renders `<div class="board">` as its root element, but `index.html` expects to morph content into `<div id="board">`. The fragment lacks `id="board"` on its root element, so Datastar's default ID-based morphing will fail to find a matching target. *(from reviewer-second-opinion, reviewer-spec-audit)*

- `tf_cli/web_ui.py:92-94` - **Stale stats after Datastar refresh**: The `refresh_board` endpoint returns only the `_board.html` fragment, but the board header in `index.html` displays counts (`{{ counts.ready }}`, etc.) that are rendered server-side and never updated during refresh. *(from reviewer-general)*

## Major (should fix)

- `tf_cli/web_ui.py:61-86` + `tf_cli/web_ui.py:123-148` - **Code duplication between `index()` and `refresh_board()`**: Both functions build identical `columns` dictionaries with the same loop logic. Extract to a shared helper like `_build_columns_data(board_view)`. *(from reviewer-general, reviewer-second-opinion)*

- `tf_cli/templates/base.html:10` - **Missing Subresource Integrity**: The Datastar CDN script lacks an `integrity` attribute. Without SRI, a compromised CDN could inject malicious JavaScript. *(from reviewer-general)*

- `tf_cli/web_ui.py:118-120` - **State-changing GET request**: Using `@get('/api/refresh')` for refresh violates REST semantics. While Datastar uses GET for actions, document this design choice or consider POST. *(from reviewer-general)*

- `tf_cli/templates/base.html:83-85` - **Unused CSS class**: `.status-blocked` is defined but never referenced in any template. *(from reviewer-general)*

- `tf_cli/web_ui.py:108` - **`ticket_detail` lacks try/except for template rendering**: Unlike the `index()` endpoint which has error handling, template rendering failures in `ticket_detail` will bubble up as unhandled exceptions. *(from reviewer-second-opinion)*

- `tf_cli/templates/ticket.html:88` + `_board.html:12,33,54,75` - **Priority rendering lacks None guard**: Renders `P{{ ticket.priority }}` without checking for None, producing "PNone" output. *(from reviewer-spec-audit, reviewer-second-opinion)*

## Minor (nice to fix)

- `tf_cli/web_ui.py:37` - **Missing return type hint**: `get_board_data()` lacks return type annotation. Should be `-> BoardView | None`. *(from reviewer-general)*

- `tf_cli/web_ui.py:20-27` - **Inconsistent repo root detection**: `_find_repo_root()` checks only for `.tf` directory, but `ui.py` version also checks for `has_agents`. *(from reviewer-general)*

- `tf_cli/web_ui.py:41` - **Error handling prints to stderr without structured context**: The `get_board_data()` error message doesn't include exception details. *(from reviewer-second-opinion)*

- `tf_cli/board_classifier.py:138-145` - **Comment/docstring drift**: Docstring says "In Progress: status == 'in_progress' and all dependencies are closed" but implementation checks blocking deps before status. *(from reviewer-general)*

## Warnings (follow-up ticket)

- `tf_cli/templates/ticket.html:95-97` - **Placeholder external tracker URL**: Hardcodes `https://tracker.example.com/{{ ticket.id }}` which will 404 for all real tickets. *(from reviewer-general)*

- `tf_cli/web_ui.py:1` - **No test coverage for web_ui.py**: No tests for `/`, `/ticket/<id>`, and `/api/refresh` endpoints. *(from reviewer-general)*

- `tf_cli/templates/ticket.html:90-93` - **Markdown not rendered**: Ticket body displayed in `<pre>` tag as raw text. Implement server-side markdown rendering. *(from reviewer-general)*

- `tf_cli/web_ui.py:1-148` - **No rate limiting on `/api/refresh` endpoint**: Could be abused for DoS by rapid clicking. *(from reviewer-second-opinion)*

- `tf_cli/web_ui.py:97` - **No input validation on `ticket_id` parameter**: No format validation (alphanumeric, length limits). *(from reviewer-second-opinion)*

## Suggestions (follow-up ticket)

- `tf_cli/templates/_board.html` - **Consider adding stable ids**: Add `id="ticket-{{ ticket.id }}"`, `id="col-ready"` for deterministic Datastar morphing. *(from reviewer-spec-audit)*

- `tf_cli/templates/_board.html` - **Consider empty state improvements**: Add action links like "Create your first ticket with `tk create`". *(from reviewer-general)*

- `tf_cli/web_ui.py:56` - **Add health check endpoint**: Simple `/health` endpoint for monitoring and container orchestration. *(from reviewer-general)*

- `tf_cli/web_ui.py` - **Centralize Datastar version**: Version "v1.0.0-RC.7" appears in both `base.html` and `web_ui.py`. *(from reviewer-second-opinion)*

- `tf_cli/templates/` - **Add data-testid or semantic IDs for E2E testing**: Improve testability with stable test IDs. *(from reviewer-second-opinion)*

- `tf_cli/templates/ticket.html:102` - **Implement server-side markdown rendering**: Use `markdown` or `mistune` library. *(from reviewer-second-opinion)*

## Summary Statistics
- Critical: 4
- Major: 6
- Minor: 4
- Warnings: 5
- Suggestions: 6

## Positive Notes
- Good use of Datastar's hypermedia approach with proper `@get` actions
- Clean Jinja2 template inheritance structure (base → index/ticket)
- Defensive programming with `{{ ticket.title or '(no title)' }}` fallbacks
- Proper lazy loading of ticket bodies in `ticket_loader.py`
- Comprehensive docstrings in `board_classifier.py`
- Responsive CSS with mobile breakpoints
- Pinned Datastar version (v1.0.0-RC.7) prevents CDN drift
- Datastar CDN correctly uses colon-delimited attributes (`data-on:click`)
- Four columns (Ready/Blocked/In Progress/Closed) implemented as required
