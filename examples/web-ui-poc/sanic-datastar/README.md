# POC: Sanic + Datastar for tf UI

## Overview

This POC demonstrates a web-native kanban board using **Sanic** (Python async web framework) and **Datastar** (hypermedia frontend framework with SSE support).

## Prerequisites

```bash
pip install sanic jinja2
```

Or using the project's venv:
```bash
source .venv/bin/activate
pip install sanic jinja2
```

## Running the POC

1. From the repo root directory, run:
```bash
cd examples/web-ui-poc/sanic-datastar
python web_app.py
```

2. Open http://127.0.0.1:8080 in your browser

## What You'll See

- Native web kanban board with 4 columns (Ready/Blocked/In Progress/Closed)
- Click tickets to see detail views
- **Datastar-powered** refresh button (no page reload)
- Bookmarkable URLs (e.g., `/ticket/pt-7t1n`)
- Responsive design

## Architecture

### Backend (Sanic)

| Route | Description |
|-------|-------------|
| `GET /` | Kanban board with all columns |
| `GET /ticket/{id}` | Individual ticket detail page |
| `GET /api/refresh` | Datastar endpoint for board refresh |

### Frontend (Datastar)

- **Datastar CDN**: Pinned to v1.0.0-RC.7
- **Attributes**: Uses colon-delimited syntax (`data-on:click`, not `data-on-click`)
- **Updates**: Server returns HTML fragments; Datastar morphs them into DOM

## File Structure

```
sanic-datastar/
├── web_app.py              # Sanic application
├── templates/
│   ├── base.html           # Base layout with Datastar CDN
│   ├── index.html          # Kanban board page
│   ├── _board.html         # Board columns (Datastar fragment)
│   └── ticket.html         # Ticket detail page
└── README.md               # This file
```

## Key Datastar Patterns

### Click to navigate
```html
<button data-on:click="@get('/ticket/pt-123')">
    View Ticket
</button>
```

### Refresh button (partial update)
```html
<button data-on:click="@get('/api/refresh')">
    Refresh
</button>

<!-- Server returns HTML that Datastar morphs into #board -->
<div id="board">...</div>
```

### Signals (reactive state)
```html
<input data-signals:search="''" data-bind:search>
<div data-text="$search"></div>
```

## Datastar Version Pinning

To avoid breaking changes, Datastar is pinned to v1.0.0-RC.7:

```html
<script src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.7/bundles/datastar.js"></script>
```

### Syntax Notes for RC.7
- **Attributes use colons**: `data-on:click` (not `data-on-click`)
- **Actions use @**: `@get('/url')`, `@post('/url')`
- **Signals use $**: `$signalName` in expressions

## Comparison with FastAPI+HTMX

| Aspect | FastAPI+HTMX | Sanic+Datastar |
|--------|--------------|----------------|
| Backend | FastAPI (Starlette) | Sanic (uvloop) |
| Frontend | HTMX | Datastar |
| Size | ~14KB | ~11KB |
| Real-time | HTMX SSE extension | Native SSE support |
| Reactivity | Server-driven | Signals + Server-driven |
| Syntax | `hx-get`, `hx-target` | `data-on:click`, morph by ID |

## Next Steps for Production

1. **Add SSE streaming** for real-time board updates
2. **Implement drag-and-drop** for ticket movement
3. **Add search/filter** using Datastar signals
4. **Dark mode toggle** using `data-class` or signals
5. **Authentication** (when needed)

## References

- Datastar: https://data-star.dev
- Sanic: https://sanic.dev
- Decision ticket: pt-sd01
- Research spike: `.tf/knowledge/topics/spike-sanic-datastar-vs-fastapi-htmx/`
