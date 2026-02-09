# Fixes: pt-1d6c

## Summary
Applied fixes for all 4 Critical issues identified in the review, plus 2 Major issues (priority None guard and code duplication).

## Critical Issues Fixed

### 1. Empty board misclassified as error (web_ui.py:52-54)
**Problem:** The `if not board_view:` check treated an empty `BoardView` (valid state with 0 tickets) as an error. `BoardView` with empty `all_tickets` list is falsy, causing 500 errors for new/empty projects.

**Fix:** Changed to explicit `if board_view is None:` check in both `index()` and `refresh_board()` endpoints. Added comprehensive docstring explaining the behavior.

**Files changed:** `tf_cli/web_ui.py`

### 2. Jinja2 autoescaping disabled, XSS vulnerability (web_ui.py:33)
**Problem:** The `Environment` was created without `select_autoescape()` or `autoescape=True`. Combined with `ticket.html` rendering `{{ ticket.body }}` directly, this allowed stored XSS attacks.

**Fix:** Added `autoescape=True` to the Jinja2 Environment constructor. This automatically escapes all HTML-sensitive characters in template variables.

**Files changed:** `tf_cli/web_ui.py`

### 3. Structural mismatch breaks Datastar morphing (_board.html:1 + index.html:137)
**Problem:** The `_board.html` fragment rendered `<div class="board">` as its root element, but `index.html` expected to morph content into `<div id="board">`. The fragment lacked `id="board"` on its root element.

**Fix:** 
- Added `id="board"` to the root div in `_board.html`
- Modified `_board.html` to include the header stats and refresh button
- Simplified `index.html` to just include the fragment
- Now the entire board (header + grid) is refreshed by Datastar, fixing the stale stats issue

**Files changed:** `tf_cli/templates/_board.html`, `tf_cli/templates/index.html`

### 4. Stale stats after Datastar refresh (web_ui.py:92-94)
**Problem:** The `refresh_board` endpoint returned only the `_board.html` fragment with columns, but the board header in `index.html` displayed counts (`{{ counts.ready }}`, etc.) that were never updated during refresh.

**Fix:** 
- Modified `_board.html` to include the header with stats
- Modified `refresh_board()` to pass `counts` to the template
- The entire `#board` div (header + grid) is now replaced on refresh

**Files changed:** `tf_cli/web_ui.py`, `tf_cli/templates/_board.html`

## Major Issues Fixed

### 5. Code duplication between index() and refresh_board()
**Problem:** Both functions built identical `columns` dictionaries with the same loop logic.

**Fix:** Extracted shared helper function `_build_columns_data(board_view)` that builds the columns dictionary. Both endpoints now use this helper.

**Files changed:** `tf_cli/web_ui.py`

### 6. Priority rendering lacks None guard
**Problem:** Templates rendered `P{{ ticket.priority }}` without checking for None, producing "PNone" output.

**Fix:** Added None guards in both `_board.html` and `ticket.html`:
```jinja2
{% if ticket.priority is not none %}
<span class="ticket-priority priority-p{{ ticket.priority }}">P{{ ticket.priority }}</span>
{% else %}
<span class="ticket-priority priority-pnone">—</span>
{% endif %}
```
Also added `.priority-pnone` CSS class in `base.html`.

**Files changed:** `tf_cli/templates/_board.html`, `tf_cli/templates/ticket.html`, `tf_cli/templates/base.html`

## Additional Improvements

- Added proper return type hint documentation for `get_board_data()`
- Added better error message in `ticket_detail` exception handler
- Updated `_board.html` docstring to explain it includes header and grid

## Verification

To verify the fixes work:

```bash
# Start the web server
tf ui --web

# Access in browser
open http://127.0.0.1:8000

# Test scenarios:
# 1. Empty project (no tickets) - should show empty board, not 500 error
# 2. Click refresh button - stats should update
# 3. XSS test - create ticket with <script>alert('xss')</script> in body, verify it's escaped
# 4. None priority - verify displays "—" instead of "PNone"
```

## Files Changed Summary

| File | Changes |
|------|---------|
| `tf_cli/web_ui.py` | Autoescape, None check, helper function, counts in refresh |
| `tf_cli/templates/_board.html` | Added id="board", header section, None guards |
| `tf_cli/templates/index.html` | Simplified to just include fragment |
| `tf_cli/templates/ticket.html` | None guard for priority |
| `tf_cli/templates/base.html` | Added .priority-pnone CSS class |
