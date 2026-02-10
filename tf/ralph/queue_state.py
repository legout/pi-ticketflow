"""Queue state snapshot helper for Ralph scheduler.

Computes ready/blocked/running/done counts from in-memory scheduler state.
Follows semantics defined in pt-m54d specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class QueueStateSnapshot:
    """Immutable snapshot of queue state at a point in time.

    Attributes:
        ready: Number of tickets that are runnable but not currently being processed.
            This excludes any tickets that are currently running.
        blocked: Number of tickets blocked by unmet dependencies (deps-only for MVP).
        running: Number of tickets currently being processed.
        done: Number of tickets completed (success or failure) during current run.
        total: Sum of all states (ready + blocked + running + done).
    """

    ready: int
    blocked: int
    running: int
    done: int
    total: int

    def __post_init__(self) -> None:
        """Validate invariant: total equals sum of all states."""
        computed_total = self.ready + self.blocked + self.running + self.done
        if computed_total != self.total:
            raise ValueError(
                f"QueueStateSnapshot invariant violated: "
                f"ready({self.ready}) + blocked({self.blocked}) + "
                f"running({self.running}) + done({self.done}) = {computed_total}, "
                f"but total={self.total}"
            )

    def __str__(self) -> str:
        """Format as: R:3 B:2 (done 1/6)"""
        return f"R:{self.ready} B:{self.blocked} (done {self.done}/{self.total})"

    def to_log_format(self) -> str:
        """Format for log lines: R:3 B:2 done:1/6"""
        return f"R:{self.ready} B:{self.blocked} done:{self.done}/{self.total}"


def get_queue_state(
    pending: set[str],
    running: set[str],
    completed: set[str],
    dep_graph: dict[str, set[str]],
) -> QueueStateSnapshot:
    """Compute queue state snapshot from scheduler in-memory state.

    Computes ready/blocked/running/done counts according to the semantics
    defined in pt-m54d:
    - Ready: pending tickets that are not blocked by unmet deps
    - Blocked: pending tickets with unmet dependencies
    - Running: tickets currently being processed
    - Done: tickets completed during current run
    - Total: sum of all states

    Args:
        pending: Set of ticket IDs in the pending queue (waiting to run).
        running: Set of ticket IDs currently being processed.
        completed: Set of ticket IDs completed in current run.
        dep_graph: Mapping of ticket ID -> set of unmet dependency IDs.
            A ticket is considered blocked if it has any entries in this map.

    Returns:
        QueueStateSnapshot with computed counts.

    Raises:
        ValueError: If any ticket appears in multiple state sets (pending,
            running, completed must be disjoint).

    Complexity: O(|pending| + |running| + |completed|)

    Example:
        >>> pending = {"T-1", "T-2", "T-3"}
        >>> running = {"T-4"}
        >>> completed = {"T-5"}
        >>> dep_graph = {"T-2": {"T-1"}}  # T-2 blocked on T-1
        >>> snapshot = get_queue_state(pending, running, completed, dep_graph)
        >>> str(snapshot)
        'R:2 B:1 (done 1/5)'
    """
    # Validate disjointness of state sets
    pending_running = pending & running
    if pending_running:
        raise ValueError(
            f"Tickets cannot be both pending and running: {pending_running}"
        )

    pending_completed = pending & completed
    if pending_completed:
        raise ValueError(
            f"Tickets cannot be both pending and completed: {pending_completed}"
        )

    running_completed = running & completed
    if running_completed:
        raise ValueError(
            f"Tickets cannot be both running and completed: {running_completed}"
        )

    # Count running and done (these are direct counts from sets)
    running_count = len(running)
    done_count = len(completed)

    # Count blocked: pending tickets with unmet dependencies
    # A ticket is blocked if it has any entries in dep_graph
    blocked_count = 0
    for ticket in pending:
        if ticket in dep_graph and dep_graph[ticket]:
            blocked_count += 1

    # Count ready: pending tickets that are not blocked
    ready_count = len(pending) - blocked_count

    # Compute total
    total_count = ready_count + blocked_count + running_count + done_count

    return QueueStateSnapshot(
        ready=ready_count,
        blocked=blocked_count,
        running=running_count,
        done=done_count,
        total=total_count,
    )


def get_queue_state_from_scheduler(
    pending: set[str],
    running: set[str],
    completed: set[str],
    dep_resolver: Optional[Callable[[str], set[str]]] = None,
) -> QueueStateSnapshot:
    """Convenience wrapper to build dep_graph from a dependency resolver.

    This is an alternative to get_queue_state() that computes the dep_graph
    internally using a resolver function, useful when the caller doesn't
    have a pre-built dep_graph.

    Args:
        pending: Set of ticket IDs in the pending queue.
        running: Set of ticket IDs currently being processed.
        completed: Set of ticket IDs completed in current run.
        dep_resolver: Optional callable that takes a ticket ID and returns
            a set of its unmet dependencies. If None, assumes no dependencies.

    Returns:
        QueueStateSnapshot with computed counts.
    """
    if dep_resolver is None:
        dep_graph = {}
    else:
        dep_graph = {ticket: dep_resolver(ticket) for ticket in pending}

    return get_queue_state(pending, running, completed, dep_graph)
