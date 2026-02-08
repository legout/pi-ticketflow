"""Textual TUI for Ticketflow.

Provides a minimal Kanban-style interface for viewing tickets.
"""

from __future__ import annotations

import sys
from typing import Optional


def main(argv: Optional[list[str]] = None) -> int:
    """Launch the Ticketflow TUI.
    
    Args:
        argv: Command line arguments (unused, for API compatibility)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Check if we're running in a TTY
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Error: tf ui requires an interactive terminal (TTY)", file=sys.stderr)
        return 1
    
    try:
        from textual.app import App
        from textual.widgets import Static, Header, Footer
    except ImportError:
        print("Error: Textual is not installed. Run: pip install textual", file=sys.stderr)
        return 1
    
    class TicketflowApp(App):
        """Minimal Textual app skeleton for Ticketflow."""
        
        CSS = """
        Screen {
            align: center middle;
        }
        #placeholder {
            width: 60;
            height: auto;
            border: solid green;
            padding: 1 2;
            text-align: center;
        }
        """
        
        BINDINGS = [
            ("q", "quit", "Quit"),
        ]
        
        def compose(self):
            """Compose the app layout."""
            yield Header()
            yield Static(
                "Ticketflow TUI\n\n"
                "Kanban board coming soon!\n\n"
                "Press 'q' to quit.",
                id="placeholder"
            )
            yield Footer()
    
    app = TicketflowApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
