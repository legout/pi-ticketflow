"""Sanic + Datastar Web Application for Ticketflow.

Provides a web-native kanban board using Sanic (backend) and Datastar (frontend hypermedia).
"""

from __future__ import annotations

import sys
from pathlib import Path

from sanic import Sanic, response
from jinja2 import Environment, FileSystemLoader

from tf_cli.board_classifier import BoardClassifier, BoardColumn
from tf_cli.ticket_loader import TicketLoader


def _find_repo_root() -> Path | None:
    """Find the repository root by looking for .tf directory."""
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        tf_dir = parent / ".tf"
        if tf_dir.is_dir():
            return parent
    return None


# Get templates directory (relative to this file)
_TEMPLATES_DIR = Path(__file__).parent / "templates"

app = Sanic("TicketflowWeb")

# Jinja2 templates with autoescape enabled for security
env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=True
)


def get_board_data():
    """Load and classify tickets for the kanban board.
    
    Returns:
        BoardView | None: The classified board view, or None if an error occurred.
        Note: An empty BoardView (0 tickets) is valid and truthy.
    """
    try:
        classifier = BoardClassifier()
        board_view = classifier.classify_all()
        return board_view
    except Exception as e:
        print(f"Error loading tickets: {e}", file=sys.stderr)
        return None


def _build_columns_data(board_view):
    """Build columns data dictionary from BoardView.
    
    Args:
        board_view: The BoardView containing classified tickets
        
    Returns:
        dict: Columns data with ready, blocked, in_progress, closed lists
    """
    columns = {
        "ready": [],
        "blocked": [],
        "in_progress": [],
        "closed": []
    }
    
    for column in BoardColumn:
        tickets = board_view.get_by_column(column)
        for ct in tickets:
            columns[column.value].append(_ticket_to_dict(ct))
    
    return columns


def _ticket_to_dict(ct):
    """Convert ClassifiedTicket to dict for templates."""
    return {
        "id": ct.id,
        "title": ct.title,
        "status": ct.ticket.status,
        "priority": ct.ticket.priority,
        "assignee": ct.ticket.assignee,
        "tags": ct.ticket.tags,
        "blocking_deps": ct.blocking_deps,
    }


@app.get("/")
async def index(request):
    """Main kanban board page."""
    board_view = get_board_data()
    
    # Check for None explicitly - empty BoardView is valid (0 tickets)
    if board_view is None:
        return response.html("<h1>Error loading tickets</h1>", status=500)
    
    columns = _build_columns_data(board_view)
    
    template = env.get_template("index.html")
    rendered = template.render(
        columns=columns,
        counts=board_view.counts,
    )
    return response.html(rendered)


@app.get("/ticket/<ticket_id>")
async def ticket_detail(request, ticket_id: str):
    """Individual ticket detail page."""
    try:
        loader = TicketLoader()
        tickets = loader.load_all()
        
        ticket_map = {t.id: t for t in tickets}
        ticket = ticket_map.get(ticket_id)
        
        if not ticket:
            return response.html(f"<h1>Ticket {ticket_id} not found</h1>", status=404)
        
        template = env.get_template("ticket.html")
        rendered = template.render(
            ticket={
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
        )
        return response.html(rendered)
    except Exception as e:
        return response.html(f"<h1>Error rendering ticket: {e}</h1>", status=500)


@app.get("/api/refresh")
async def refresh_board(request):
    """Datastar endpoint to refresh the kanban board.
    
    Returns HTML fragment that Datastar will morph into the DOM.
    Includes both the board header (with counts) and the board grid
    to keep stats synchronized.
    """
    board_view = get_board_data()
    
    # Check for None explicitly - empty BoardView is valid
    if board_view is None:
        return response.html("<p class='error'>Error loading tickets</p>")
    
    columns = _build_columns_data(board_view)
    
    template = env.get_template("_board.html")
    rendered = template.render(
        columns=columns,
        counts=board_view.counts,
    )
    return response.html(rendered)


def run_web_server(host: str = "127.0.0.1", port: int = 8000) -> int:
    """Run the Sanic web server.
    
    Args:
        host: Host to bind to (default: 127.0.0.1 for security)
        port: Port to listen on (default: 8000)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Sanic handles Ctrl+C gracefully by default
    try:
        print(f"Starting Ticketflow Web UI on http://{host}:{port}", file=sys.stderr)
        print("Press Ctrl+C to stop the server", file=sys.stderr)
        print(f"Datastar version: v1.0.0-RC.7", file=sys.stderr)
        
        app.run(
            host=host,
            port=port,
            access_log=True,  # Enable access logging
            single_process=True,  # Single process to avoid worker issues
        )
        return 0
    except KeyboardInterrupt:
        print("\nServer stopped", file=sys.stderr)
        return 0
    except OSError as e:
        if e.errno == 98 or e.errno == 48:  # Address already in use (Linux/Mac)
            print(f"Error: Port {port} is already in use", file=sys.stderr)
            print(f"Try using a different port with --port", file=sys.stderr)
        else:
            print(f"Error starting server: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
