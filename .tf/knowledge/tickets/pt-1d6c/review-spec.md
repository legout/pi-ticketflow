# Review (Spec Audit): pt-1d6c

## Overall Assessment
Core board rendering (4 columns, ticket cards, priority badges, Datastar attribute syntax, and pinned CDN) is implemented and matches the POC. The biggest spec risk is whether the Datastar refresh endpoint actually morphs the intended part of the DOM (the board) since the refresh response lacks a stable target element/id; if refresh does not update the board in practice, an explicit acceptance criterion is not met.

## Critical (must fix)
- `tf_cli/templates/index.html:137-145` + `tf_cli/web_ui.py:123-148` + `tf_cli/templates/_board.html:1-83` - **Refresh may not morph the board as required.** The ticket requires a manual refresh button using `data-on:click="@get('/api/refresh')"` and notes that “Backend endpoints return HTML fragments; Datastar morphs them into DOM” and “For partial board refresh, return only the board HTML fragment.” The `/api/refresh` endpoint returns `_board.html`, but `_board.html` renders only `<div class="board">…</div>` and does not include an element with `id="board"` (the target container in `index.html`). There are also no stable ids on columns/cards (unlike the ticket’s example pattern), which increases the chance Datastar can’t reliably morph the correct DOM subtree. If Datastar’s default `@get` morph behavior is id-based (as implied by the ticket example/POC README wording), the refresh button will fetch HTML but fail to update the displayed board.

## Major (should fix)
- `.tf/knowledge/tickets/pt-1d6c/implementation.md:24-33` - The implementation write-up marks “Use Datastar's data-signals” as ✅, but the web board templates do not use `data-signals` at all (only `data-on:click`). The acceptance criterion is conditional (“if needed”), so the product may still be OK, but the implementation record is inaccurate for this criterion and could mislead future work.

## Minor (nice to fix)
- `tf_cli/templates/_board.html:12-13` (and similar at `33-34`, `54-55`, `75-76`) - Priority badge rendering does not guard against missing/None priority values. If a ticket lacks `priority`, the UI will render `PNone` and a CSS class like `priority-pNone`, which does not satisfy the “P0–P4” labeling intent.

## Warnings (follow-up ticket)
- `tf_cli/web_ui.py:33-35` + templates - Jinja2 `Environment(...)` is created without autoescaping (`select_autoescape`), which can become an XSS vector if ticket fields contain unsafe content. Not in the explicit acceptance criteria, but relevant for a browser UI.

## Suggestions (follow-up ticket)
- `tf_cli/templates/_board.html` - Consider adding stable ids (e.g., `id="ticket-{{ ticket.id }}"`, `id="col-ready"`) consistent with the ticket’s “Example Template Pattern” to make Datastar morphing deterministic and to support future partial updates (single-card refresh, drag/drop, etc.).
- `tf_cli/web_ui.py:61-86` - Consider returning/patching the counts (`counts.ready`, etc.) during refresh as well (either by including them in the refreshed fragment or splitting into separate fragments), so the header stats don’t become stale after a board refresh.

## Positive Notes
- `tf_cli/templates/base.html:8-9` - Datastar CDN is pinned to `v1.0.0-RC.7` as required.
- `tf_cli/templates/_board.html:1-83` - Four columns (Ready/Blocked/In Progress/Closed) and empty states are present.
- `tf_cli/web_ui.py:37-86` + `tf_cli/board_classifier.py` + `tf_cli/ticket_loader.py` - Board data is produced via the existing `BoardClassifier`/`TicketLoader` pipeline.
- `tf_cli/templates/_board.html:9,30,51,72` - Ticket cards use colon-delimited Datastar attributes (`data-on:click`) and navigate to `/ticket/<id>`.

## Summary Statistics
- Critical: 1
- Major: 1
- Minor: 1
- Warnings: 1
- Suggestions: 2

## Spec Coverage
- Spec/plan sources consulted: 
  - `tk show pt-1d6c` (acceptance criteria + Datastar notes)
  - `.tf/knowledge/tickets/pt-1d6c/implementation.md`
  - `tk show pt-sd01` (stack decision + Datastar syntax pin)
  - `.tf/knowledge/topics/seed-tf-ui-web-app/*` (seed context)
  - `examples/web-ui-poc/sanic-datastar/README.md` (POC expectations)
- Missing specs: none
