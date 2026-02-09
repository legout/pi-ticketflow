"""Sanic + Datastar Web Application for Ticketflow.

Provides a web-native kanban board using Sanic (backend) and Datastar (frontend hypermedia).

Dependencies:
    - datastar-py>=0.7.0,<0.8.0: Python SDK for Datastar SSE responses. Pinned to match the
      Datastar JS bundle version (v1.0.0-RC.7) loaded from CDN in templates/base.html.
      Version 0.7.0 is used because 0.8.0 requires Python >=3.10 while this project
      supports Python >=3.9. Both 0.7.0 and 0.8.0 are compatible with Datastar JS v1.0.0-RC.7.
"""

from __future__ import annotations

import sys
from pathlib import Path

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from sanic import Sanic, response
from jinja2 import Environment, FileSystemLoader

# datastar-py imports for SSE streaming support
try:
    from datastar_py.sanic import datastar_respond, read_signals
    from datastar_py import ServerSentEventGenerator
    DATASTAR_AVAILABLE = True
except ImportError:
    DATASTAR_AVAILABLE = False
    datastar_respond = None
    ServerSentEventGenerator = None
    read_signals = None

from tf_cli.board_classifier import BoardClassifier, BoardColumn
from tf_cli.ticket_loader import TicketLoader
from tf_cli.ui import TopicIndexLoader, TopicIndexLoadError, resolve_knowledge_dir, _find_repo_root


# Get templates directory (relative to this file)
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_STATIC_DIR = Path(__file__).parent / "static"

# Verify static directory exists at startup for better error messages
if not _STATIC_DIR.exists():
    print(f"Warning: Static directory does not exist: {_STATIC_DIR}", file=sys.stderr)

app = Sanic("TicketflowWeb")

# Serve static files (CSS, etc.) from the static directory
app.static("/static", str(_STATIC_DIR), name="static")

# Jinja2 templates with autoescape enabled for security
env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=True
)

# Markdown extensions configuration for document rendering
# Note: Raw HTML is disabled for security (prevents XSS via <script> tags)
MD_EXTENSIONS = [
    FencedCodeExtension(),
    TableExtension(),
    TocExtension(),
    CodeHiliteExtension(
        css_class="highlight",
        guess_lang=True,
        use_pygments=True,
    ),
]

# Reusable Markdown instance (thread-safe for single-process server)
_md = markdown.Markdown(extensions=MD_EXTENSIONS)


def _render_markdown(content: str) -> str:
    """Render markdown content to HTML with syntax highlighting.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Rendered HTML string with raw HTML escaped for security
    """
    _md.reset()
    # Escape raw HTML to prevent XSS attacks
    # This ensures <script> and other HTML tags are rendered as text, not executed
    import html
    content = html.escape(content)
    return _md.convert(content)


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


def _build_columns_data(board_view, search_query: str = ""):
    """Build columns data dictionary from BoardView.

    Args:
        board_view: The BoardView containing classified tickets
        search_query: Optional search query to filter tickets by title

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
            # Apply search filter if provided (case-insensitive contains match)
            if search_query:
                title = (ct.title or "").lower()
                if search_query not in title:
                    continue
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


def _topic_to_dict(topic):
    """Convert Topic to dict for templates."""
    return {
        "id": topic.id,
        "title": topic.title,
        "topic_type": topic.topic_type,
        "keywords": topic.keywords,
        "has_overview": topic.overview is not None and topic.overview.exists,
        "has_sources": topic.sources is not None and topic.sources.exists,
        "has_plan": topic.plan is not None and topic.plan.exists,
        "has_backlog": topic.backlog is not None and topic.backlog.exists,
        "available_docs": list(topic.available_docs.keys()),
    }


def get_topics_data(search_query: str = ""):
    """Load topics for the topic browser.
    
    Args:
        search_query: Optional search query to filter topics
        
    Returns:
        tuple: (topics_by_type dict, total_count) or (None, 0) on error
    """
    # Sanitize search query: trim and limit length
    search_query = search_query.strip()[:100] if search_query else ""
    
    try:
        loader = TopicIndexLoader()
        loader.load()
        
        # Search if query provided
        if search_query:
            topics = loader.search(search_query)
        else:
            topics = loader.get_all()
        
        # Group by type
        topics_by_type = {
            "seed": [],
            "plan": [],
            "spike": [],
            "baseline": [],
            "unknown": [],
        }
        
        for topic in topics:
            topics_by_type[topic.topic_type].append(_topic_to_dict(topic))
        
        # Sort each group by title
        for topic_type in topics_by_type:
            topics_by_type[topic_type].sort(key=lambda t: t["title"].lower())
        
        return topics_by_type, len(topics)
    except TopicIndexLoadError as e:
        print(f"Error loading topics: {e}", file=sys.stderr)
        return None, 0
    except Exception as e:
        print(f"Unexpected error loading topics: {e}", file=sys.stderr)
        return None, 0


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

    Reads the `$search` signal from Datastar to filter tickets by title.
    """
    board_view = get_board_data()

    # Check for None explicitly - empty BoardView is valid
    if board_view is None:
        return response.html("<p class='error'>Error loading tickets</p>")

    # Read signals from Datastar request for filtering
    search_query = ""
    if DATASTAR_AVAILABLE and read_signals is not None:
        signals = await read_signals(request)
        if signals:
            search_query = signals.get("$search", "").strip().lower()

    columns = _build_columns_data(board_view, search_query=search_query)

    template = env.get_template("_board.html")
    rendered = template.render(
        columns=columns,
        counts=board_view.counts,
    )
    return response.html(rendered)


@app.get("/api/stream")
async def stream_board(request):
    """SSE streaming endpoint for live board updates.
    
    Streams patch_elements events periodically to update the board
    without requiring manual refresh. Client subscribes on page load
    via data-init="@get('/api/stream')".
    
    Handles client disconnects gracefully to prevent server crashes.
    Update frequency is conservative (2s) to avoid busy loops.
    """
    import asyncio
    
    if not DATASTAR_AVAILABLE:
        return response.html("<p class='error'>datastar-py not available</p>", status=503)
    
    # Get streaming response object for SSE
    resp = await datastar_respond(request)
    
    try:
        while True:
            # Load fresh board data
            board_view = get_board_data()
            
            if board_view is not None:
                columns = _build_columns_data(board_view)
                
                # Render board fragment
                template = env.get_template("_board.html")
                board_html = template.render(
                    columns=columns,
                    counts=board_view.counts,
                )
                
                # Send SSE event to patch the board
                event = ServerSentEventGenerator.patch_elements(
                    elements=board_html,
                    selector="#board"
                )
                await resp.send(event)
            
            # Wait before next update (conservative 2s interval)
            await asyncio.sleep(2)
            
    except asyncio.CancelledError:
        # Client disconnected - clean exit
        pass
    except Exception as e:
        # Log error but don't crash the server
        print(f"Error in stream_board: {e}", file=sys.stderr)
        # Try to send error event if connection still open
        try:
            error_event = ServerSentEventGenerator.patch_elements(
                elements=f"<p class='error'>Stream error: {e}</p>",
                selector="#board"
            )
            await resp.send(error_event)
        except Exception:
            pass  # Connection likely closed


@app.get("/topics")
async def topics_browser(request):
    """Topic browser page for navigating knowledge base topics."""
    search_query = request.args.get("search", [""])[0]
    topics_by_type, total_count = get_topics_data(search_query)
    
    if topics_by_type is None:
        return response.html("<h1>Error loading topics</h1>", status=500)
    
    template = env.get_template("topics.html")
    rendered = template.render(
        topics_by_type=topics_by_type,
        total_count=total_count,
        search_query=search_query,
    )
    return response.html(rendered)


@app.get("/api/topics")
async def api_topics(request):
    """Datastar endpoint for topic search/filter.
    
    Returns HTML fragment with filtered topic list.
    """
    search_query = request.args.get("search", [""])[0]
    topics_by_type, total_count = get_topics_data(search_query)
    
    if topics_by_type is None:
        return response.html("<p class='error'>Error loading topics</p>")
    
    template = env.get_template("_topics_list.html")
    rendered = template.render(
        topics_by_type=topics_by_type,
        total_count=total_count,
        search_query=search_query,
    )
    return response.html(rendered)


@app.get("/topic/<topic_id>")
async def topic_detail(request, topic_id: str):
    """Individual topic detail page."""
    try:
        loader = TopicIndexLoader()
        loader.load()
        
        topic = loader.get_by_id(topic_id)
        
        if not topic:
            return response.html(f"<h1>Topic {topic_id} not found</h1>", status=404)
        
        template = env.get_template("topic_detail.html")
        rendered = template.render(
            topic=_topic_to_dict(topic),
            topic_obj=topic,  # Pass original topic object for doc paths
        )
        return response.html(rendered)
    except Exception as e:
        return response.html(f"<h1>Error rendering topic: {e}</h1>", status=500)


@app.get("/topic/<topic_id>/doc/<doc_type>")
async def topic_document(request, topic_id: str, doc_type: str):
    """Document viewer for topic documents with inline rendering.
    
    Args:
        topic_id: The topic ID (e.g., "seed-add-versioning")
        doc_type: Document type - overview, sources, plan, or backlog
    """
    # Normalize and validate doc_type (case-insensitive)
    doc_type = doc_type.lower()
    valid_doc_types = ["overview", "sources", "plan", "backlog"]
    if doc_type not in valid_doc_types:
        return response.html(
            f"<h1>Invalid document type: {doc_type}</h1>",
            status=400
        )
    
    try:
        loader = TopicIndexLoader()
        loader.load()
        
        topic = loader.get_by_id(topic_id)
        
        if not topic:
            return response.html(f"<h1>Topic {topic_id} not found</h1>", status=404)
        
        # Get the document
        doc = getattr(topic, doc_type, None)
        
        # Check if document exists
        content_html = None
        content_exists = False
        read_error = None
        
        if doc and doc.exists:
            knowledge_dir = resolve_knowledge_dir()
            doc_path = (knowledge_dir / doc.path).resolve()
            
            # Security: Validate path is within knowledge_dir (prevents path traversal)
            if not str(doc_path).startswith(str(knowledge_dir.resolve())):
                return response.html("<h1>Access denied</h1>", status=403)
            
            try:
                content = doc_path.read_text(encoding="utf-8")
                content_html = _render_markdown(content)
                content_exists = True
            except FileNotFoundError:
                # Document was listed in index but file is missing
                content_exists = False
            except (IOError, OSError) as e:
                # Actual error reading file
                read_error = str(e)
                print(f"Error reading document {doc_path}: {e}", file=sys.stderr)
        
        # Check if this is a Datastar fragment request (has target header or fragment param)
        is_fragment = request.headers.get("datastar-request") == "true" or \
                      request.args.get("fragment", ["false"])[0].lower() == "true"
        
        # Prepare document type info for template (avoids hardcoding in templates)
        doc_type_info = [
            {"type": "overview", "icon": "📄", "title": "Overview"},
            {"type": "sources", "icon": "📚", "title": "Sources"},
            {"type": "plan", "icon": "📋", "title": "Plan"},
            {"type": "backlog", "icon": "✅", "title": "Backlog"},
        ]
        
        # Pre-compute document existence to avoid getattr in template
        doc_availability = {
            dt: getattr(topic, dt, None) is not None and getattr(topic, dt).exists
            for dt in valid_doc_types
        }
        
        if is_fragment:
            # Return just the document viewer fragment for Datastar morphing
            template = env.get_template("_doc_viewer.html")
            rendered = template.render(
                topic=_topic_to_dict(topic),
                doc_type=doc_type,
                content_html=content_html,
                content_exists=content_exists,
                read_error=read_error,
                doc_type_info=doc_type_info,
                doc_availability=doc_availability,
            )
        else:
            # Return full page
            template = env.get_template("doc_viewer.html")
            rendered = template.render(
                topic=_topic_to_dict(topic),
                doc_type=doc_type,
                content_html=content_html,
                content_exists=content_exists,
                read_error=read_error,
                doc_type_info=doc_type_info,
                doc_availability=doc_availability,
            )
        
        return response.html(rendered)
    except Exception as e:
        return response.html(f"<h1>Error rendering document: {e}</h1>", status=500)


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
