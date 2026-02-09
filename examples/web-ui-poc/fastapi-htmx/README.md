# POC: FastAPI + HTMX for tf UI

## Overview
This POC demonstrates a web-native kanban board using FastAPI and HTMX.

## Prerequisites
```bash
pip install fastapi uvicorn jinja2
```

Or using the project's venv:
```bash
source .venv/bin/activate
pip install fastapi uvicorn jinja2
```

## Running the POC

1. From the repo root directory, run:
```bash
cd .tf/knowledge/tickets/pt-7t1n/poc/fastapi-htmx
python web_app.py
```

2. Open http://127.0.0.1:8080 in your browser

## What You'll See
- Native web kanban board with 4 columns
- Click tickets to see detail views
- HTMX-powered refresh button (no page reload)
- Bookmarkable URLs (e.g., `/ticket/pt-7t1n`)
- Responsive design that works on mobile

## Architecture

### Backend (FastAPI)
- `GET /` - Kanban board with all columns
- `GET /ticket/{id}` - Individual ticket detail page
- `GET /api/refresh` - HTMX endpoint for partial board refresh

### Frontend (HTMX + Jinja2)
- Server-rendered HTML templates
- HTMX for dynamic updates without full page reloads
- CSS Grid for responsive kanban layout
- No JavaScript framework needed

## File Structure
```
fastapi-htmx/
├── web_app.py           # FastAPI application
├── templates/
│   ├── base.html        # Base layout template
│   ├── index.html       # Kanban board page
│   ├── _board.html      # Board columns (HTMX fragment)
│   └── ticket.html      # Ticket detail page
└── README.md            # This file
```

## Observations

### Pros
- ✅ Native web UX with bookmarkable URLs
- ✅ Mobile responsive design
- ✅ Works without JavaScript (graceful degradation)
- ✅ Standard web patterns (easy to hire for)
- ✅ Easy to extend with multi-user features later
- ✅ Better accessibility (semantic HTML)

### Cons
- ❌ Separate codebase from TUI (duplication)
- ❌ More initial work to implement
- ❌ Need to maintain two UI implementations
- ❌ HTMX learning curve for the team

## Verdict
Best for: Long-term web-first strategy, public-facing tools, accessibility requirements
Not ideal for: Quick prototypes, teams wanting single codebase

## Next Steps for Production
1. Add real-time updates via Server-Sent Events
2. Implement drag-and-drop for ticket movement
3. Add search/filter functionality
4. Dark mode toggle
5. Authentication (when needed)
