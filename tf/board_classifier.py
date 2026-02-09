"""Board classification logic for Kanban-style ticket board.

Provides Ready/Blocked/In Progress/Closed classification based on ticket
dependencies and status, computed locally without subprocess calls.

Classification Rules:
- Closed: status == "closed" (regardless of dependencies)
- In Progress: status == "in_progress" and all dependencies are closed
- Blocked: status in {open, in_progress} and any dependency is not closed
- Ready: status == "open" and all dependencies are closed
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from tf.ticket_loader import Ticket, TicketLoader


class BoardColumn(Enum):
    """Kanban board columns."""
    READY = "ready"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


@dataclass
class ClassifiedTicket:
    """A ticket with its board column classification.
    
    Attributes:
        ticket: The underlying Ticket object
        column: The board column this ticket belongs to
        blocking_deps: List of dependency IDs that are blocking this ticket
                      (only populated for BLOCKED tickets)
    """
    ticket: Ticket
    column: BoardColumn
    blocking_deps: list[str] = field(default_factory=list)
    
    @property
    def id(self) -> str:
        """Get ticket ID."""
        return self.ticket.id
    
    @property
    def status(self) -> str:
        """Get ticket status."""
        return self.ticket.status
    
    @property
    def title(self) -> str:
        """Get ticket title."""
        return self.ticket.title
    
    def is_ready(self) -> bool:
        """Check if ticket is in Ready column."""
        return self.column == BoardColumn.READY
    
    def is_blocked(self) -> bool:
        """Check if ticket is in Blocked column."""
        return self.column == BoardColumn.BLOCKED
    
    def is_in_progress(self) -> bool:
        """Check if ticket is in In Progress column."""
        return self.column == BoardColumn.IN_PROGRESS
    
    def is_closed(self) -> bool:
        """Check if ticket is in Closed column."""
        return self.column == BoardColumn.CLOSED


class BoardClassifier:
    """Classifies tickets into Kanban board columns.
    
    This classifier implements the MVP rule for mapping tickets into
    Ready/Blocked/In Progress/Closed columns based on status and dependencies.
    
    The classification is performed locally without spawning subprocesses
    (no `tk ready` calls), making it suitable for UI rendering.
    
    Classification Rules:
    - Closed: status == "closed"
    - In Progress: status == "in_progress"  
    - Blocked: status in {open, in_progress} and any dependency is not closed
    - Ready: status in {open, in_progress} and all dependencies are closed
    
    Example:
        >>> classifier = BoardClassifier()
        >>> board = classifier.classify_all()
        >>> ready_tickets = board.get_by_column(BoardColumn.READY)
        >>> for t in ready_tickets:
        ...     print(f"{t.id}: {t.title}")
    """
    
    def __init__(self, tickets_dir: Optional[Path] = None, loader: Optional[TicketLoader] = None):
        """Initialize the classifier.
        
        Args:
            tickets_dir: Optional path to tickets directory.
                        If not provided, resolves automatically.
            loader: Optional pre-configured TicketLoader instance.
                   If provided, tickets_dir is ignored.
        """
        self.loader = loader or TicketLoader(tickets_dir)
        self._classified: list[ClassifiedTicket] = []
        self._by_column: dict[BoardColumn, list[ClassifiedTicket]] = {
            col: [] for col in BoardColumn
        }
        self._by_id: dict[str, ClassifiedTicket] = {}
    
    def classify_all(self) -> "BoardView":
        """Classify all tickets and return a BoardView.
        
        Returns:
            BoardView containing all classified tickets.
            
        Raises:
            Exception: If ticket loading fails (propagated from TicketLoader).
        """
        tickets = self.loader.load_all()
        return self._classify_tickets(tickets)
    
    def _classify_tickets(self, tickets: list[Ticket]) -> "BoardView":
        """Classify a list of tickets.
        
        Args:
            tickets: List of tickets to classify
            
        Returns:
            BoardView containing classified tickets
        """
        # Build status lookup for dependency checking
        status_by_id: dict[str, str] = {t.id: t.status for t in tickets}
        
        self._classified = []
        self._by_column = {col: [] for col in BoardColumn}
        self._by_id = {}
        
        for ticket in tickets:
            classified = self._classify_single(ticket, status_by_id)
            self._classified.append(classified)
            self._by_column[classified.column].append(classified)
            self._by_id[classified.id] = classified
        
        # Sort each column by priority (if available) then ID
        for column in BoardColumn:
            self._by_column[column].sort(
                key=lambda ct: (-(ct.ticket.priority or 0), ct.id)
            )

        return BoardView(self._classified, self._by_column, self._by_id)
    
    def _classify_single(self, ticket: Ticket, status_by_id: dict[str, str]) -> ClassifiedTicket:
        """Classify a single ticket.
        
        Args:
            ticket: The ticket to classify
            status_by_id: Lookup dict mapping ticket IDs to their status
            
        Returns:
            ClassifiedTicket with column assignment
        """
        status = (ticket.status or "").lower()
        
        # Rule 1: Closed tickets go to Closed column (regardless of deps)
        if status == "closed":
            return ClassifiedTicket(ticket, BoardColumn.CLOSED)
        
        # For open/in_progress tickets, check dependencies first
        # (blocked check applies to both open and in_progress statuses)
        blocking_deps = self._find_blocking_deps(ticket, status_by_id)
        
        # Rule 2: If any dependency is not closed, ticket is Blocked
        if blocking_deps:
            return ClassifiedTicket(ticket, BoardColumn.BLOCKED, blocking_deps)
        
        # Rule 3: In Progress status (and no blocking deps) goes to In Progress column
        if status == "in_progress":
            return ClassifiedTicket(ticket, BoardColumn.IN_PROGRESS)
        
        # Rule 4: Open status (and no blocking deps) goes to Ready column
        if status == "open":
            return ClassifiedTicket(ticket, BoardColumn.READY)
        
        # Unknown status - treat as Ready (no blocking deps)
        return ClassifiedTicket(ticket, BoardColumn.READY)
    
    def _find_blocking_deps(self, ticket: Ticket, status_by_id: dict[str, str]) -> list[str]:
        """Find dependencies that are blocking this ticket.
        
        A dependency is blocking if it's not in "closed" status.
        
        Args:
            ticket: The ticket to check
            status_by_id: Lookup dict mapping ticket IDs to their status
            
        Returns:
            List of blocking dependency IDs
        """
        blocking = []
        for dep_id in ticket.deps:
            dep_status = status_by_id.get(dep_id, "unknown").lower()
            if dep_status != "closed":
                blocking.append(dep_id)
        return blocking


@dataclass
class BoardView:
    """A view of the Kanban board with classified tickets.
    
    This is an immutable snapshot of the board state at classification time.
    
    Attributes:
        all_tickets: List of all classified tickets
        _by_column: Internal mapping of columns to tickets
        _by_id: Internal mapping of ticket IDs to classified tickets
    """
    all_tickets: list[ClassifiedTicket]
    _by_column: dict[BoardColumn, list[ClassifiedTicket]]
    _by_id: dict[str, ClassifiedTicket]
    
    def get_by_column(self, column: BoardColumn) -> list[ClassifiedTicket]:
        """Get all tickets in a specific column.
        
        Args:
            column: The board column to query
            
        Returns:
            List of tickets in that column (sorted by priority, then ID)
        """
        return self._by_column.get(column, []).copy()
    
    def get_by_id(self, ticket_id: str) -> Optional[ClassifiedTicket]:
        """Get a classified ticket by ID.
        
        Args:
            ticket_id: The ticket ID to look up
            
        Returns:
            The classified ticket if found, None otherwise
        """
        return self._by_id.get(ticket_id)
    
    def get_ready(self) -> list[ClassifiedTicket]:
        """Get all Ready tickets."""
        return self.get_by_column(BoardColumn.READY)
    
    def get_blocked(self) -> list[ClassifiedTicket]:
        """Get all Blocked tickets."""
        return self.get_by_column(BoardColumn.BLOCKED)
    
    def get_in_progress(self) -> list[ClassifiedTicket]:
        """Get all In Progress tickets."""
        return self.get_by_column(BoardColumn.IN_PROGRESS)
    
    def get_closed(self) -> list[ClassifiedTicket]:
        """Get all Closed tickets."""
        return self.get_by_column(BoardColumn.CLOSED)
    
    @property
    def counts(self) -> dict[str, int]:
        """Get ticket counts by column.
        
        Returns:
            Dictionary mapping column names to ticket counts
        """
        return {
            "ready": len(self._by_column[BoardColumn.READY]),
            "blocked": len(self._by_column[BoardColumn.BLOCKED]),
            "in_progress": len(self._by_column[BoardColumn.IN_PROGRESS]),
            "closed": len(self._by_column[BoardColumn.CLOSED]),
        }
    
    @property
    def total(self) -> int:
        """Get total number of tickets."""
        return len(self.all_tickets)
    
    def filter_by_tag(self, tag: str) -> "BoardView":
        """Create a filtered view containing only tickets with a specific tag.
        
        Args:
            tag: The tag to filter by
            
        Returns:
            A new BoardView with filtered tickets
        """
        filtered = [ct for ct in self.all_tickets if tag in ct.ticket.tags]
        return self._create_filtered_view(filtered)
    
    def filter_by_assignee(self, assignee: str) -> "BoardView":
        """Create a filtered view containing only tickets assigned to a user.
        
        Args:
            assignee: The assignee username to filter by
            
        Returns:
            A new BoardView with filtered tickets
        """
        filtered = [ct for ct in self.all_tickets if ct.ticket.assignee == assignee]
        return self._create_filtered_view(filtered)
    
    def search(self, query: str) -> "BoardView":
        """Create a filtered view containing tickets matching a search query.
        
        Searches in ticket ID, title, and tags (case-insensitive substring match).
        
        Args:
            query: The search query string
            
        Returns:
            A new BoardView with matching tickets
        """
        query_lower = query.lower()
        filtered = []
        
        for ct in self.all_tickets:
            if query_lower in ct.id.lower():
                filtered.append(ct)
            elif query_lower in ct.title.lower():
                filtered.append(ct)
            elif any(query_lower in tag.lower() for tag in ct.ticket.tags):
                filtered.append(ct)
        
        return self._create_filtered_view(filtered)
    
    def _create_filtered_view(self, filtered: list[ClassifiedTicket]) -> "BoardView":
        """Create a new BoardView from a filtered list of tickets.
        
        Args:
            filtered: The filtered list of classified tickets
            
        Returns:
            A new BoardView
        """
        by_column: dict[BoardColumn, list[ClassifiedTicket]] = {
            col: [] for col in BoardColumn
        }
        by_id: dict[str, ClassifiedTicket] = {}
        
        for ct in filtered:
            by_column[ct.column].append(ct)
            by_id[ct.id] = ct
        
        return BoardView(filtered, by_column, by_id)


def classify_tickets(tickets: list[Ticket]) -> BoardView:
    """Convenience function to classify a list of tickets.
    
    Args:
        tickets: List of tickets to classify
        
    Returns:
        BoardView containing classified tickets
        
    Example:
        >>> from tf.ticket_loader import TicketLoader
        >>> loader = TicketLoader()
        >>> tickets = loader.load_all()
        >>> board = classify_tickets(tickets)
        >>> print(f"Ready: {board.counts['ready']}")
    """
    # Create classifier without loader to avoid unnecessary initialization
    classifier = BoardClassifier.__new__(BoardClassifier)
    return classifier._classify_tickets(tickets)


def format_board_summary(board: BoardView) -> str:
    """Format a board view as a text summary.
    
    Args:
        board: The board view to format
        
    Returns:
        Formatted string showing column counts and ticket lists
    """
    lines = [
        "Board Summary",
        "=" * 50,
        "",
    ]
    
    for column in [BoardColumn.READY, BoardColumn.BLOCKED, 
                   BoardColumn.IN_PROGRESS, BoardColumn.CLOSED]:
        tickets = board.get_by_column(column)
        lines.append(f"[{column.value.upper()}] ({len(tickets)} tickets)")
        
        for ct in tickets[:10]:  # Show first 10
            priority_indicator = f"[P{ct.ticket.priority}] " if ct.ticket.priority else ""
            lines.append(f"  • {ct.id}: {priority_indicator}{ct.title[:50]}")
            if ct.blocking_deps:
                lines.append(f"    blocked by: {', '.join(ct.blocking_deps)}")
        
        if len(tickets) > 10:
            lines.append(f"  ... and {len(tickets) - 10} more")
        
        lines.append("")
    
    return "\n".join(lines)