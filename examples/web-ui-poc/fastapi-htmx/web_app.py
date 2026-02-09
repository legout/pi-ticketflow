"""FastAPI + HTMX Web Application POC for Ticketflow.

This is a proof-of-concept showing a web-native kanban board
using FastAPI and HTMX for server-rendered dynamic updates.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Annotated, Optional, Union


def _find_repo_root() -> Optional[Path]:
    """Find the repository root by looking for .tf directory."""
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        tf_dir = parent / ".tf"
        if tf_dir.is_dir():
            return parent
    return None


# Add repo root to path for imports
REPO_ROOT = _find_repo_root()
if REPO_ROOT:
    sys.path.insert(0, str(REPO_ROOT))
else:
    # Fallback: use relative path resolution
    REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent

from fastapi import FastAPI, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tf_cli.board_classifier import BoardClassifier, BoardColumn
from tf_cli.ticket_loader import TicketLoader

app = FastAPI(title="Ticketflow Web POC")

# Templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Static files (if needed)
# app.mount("/static", StaticFiles(directory="static"), name="static")


def get_board_data():
    """Load and classify tickets for the kanban board."""
    try:
        classifier = BoardClassifier()
        board_view = classifier.classify_all()
        return board_view
    except Exception as e:
        print(f"Error loading tickets: {e}")
        return None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main kanban board page."""
    board_view = get_board_data()
    
    if not board_view:
        return HTMLResponse(content="<h1>Error loading tickets</h1>", status_code=500)
    
    # Organize tickets by column
    columns = {
        "ready": [],
        "blocked": [],
        "in_progress": [],
        "closed": []
    }
    
    for column in BoardColumn:
        tickets = board_view.get_by_column(column)
        for ct in tickets:
            columns[column.value].append({
                "id": ct.id,
                "title": ct.title,
                "status": ct.ticket.status,
                "priority": ct.ticket.priority,
                "assignee": ct.ticket.assignee,
                "tags": ct.ticket.tags,
                "blocking_deps": ct.blocking_deps,
            })
    
    counts = board_view.counts
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "columns": columns,
        "counts": counts,
    })


@app.get("/ticket/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(request: Request, ticket_id: str):
    """Individual ticket detail page."""
    try:
        loader = TicketLoader()
        tickets = loader.load_all()
        
        # Build lookup dict for O(1) access
        ticket_map = {t.id: t for t in tickets}
        ticket = ticket_map.get(ticket_id)
        
        if not ticket:
            return HTMLResponse(content=f"<h1>Ticket {ticket_id} not found</h1>", status_code=404)
        
        return templates.TemplateResponse("ticket.html", {
            "request": request,
            "ticket": {
                "id": ticket.id,
                "title": ticket.title,
                "status": ticket.status,
                "priority": ticket.priority,
                "assignee": ticket.assignee,
                "tags": ticket.tags,
                "deps": ticket.deps,
                "links": ticket.links,
                "external_ref": ticket.external_ref,
                "body": ticket.body,
                "created": ticket.created,
            }
        })
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {e}</h1>", status_code=500)


@app.get("/api/refresh", response_class=HTMLResponse)
async def refresh_board(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    """HTMX endpoint to refresh the kanban board."""
    board_view = get_board_data()
    
    if not board_view:
        return HTMLResponse(content="<p class='error'>Error loading tickets</p>")
    
    # Organize tickets by column
    columns = {
        "ready": [],
        "blocked": [],
        "in_progress": [],
        "closed": []
    }
    
    for column in BoardColumn:
        tickets = board_view.get_by_column(column)
        for ct in tickets:
            columns[column.value].append({
                "id": ct.id,
                "title": ct.title,
                "status": ct.ticket.status,
                "priority": ct.ticket.priority,
                "assignee": ct.ticket.assignee,
                "tags": ct.ticket.tags,
                "blocking_deps": ct.blocking_deps,
            })
    
    if hx_request:
        # Return just the board columns HTML fragment
        return templates.TemplateResponse("_board.html", {
            "request": request,
            "columns": columns,
        })
    
    # Full page
    return templates.TemplateResponse("index.html", {
        "request": request,
        "columns": columns,
        "counts": board_view.counts,
    })


if __name__ == "__main__":
    import uvicorn
    print("Starting Ticketflow Web POC on http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)
