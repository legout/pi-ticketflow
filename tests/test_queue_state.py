"""Unit tests for QueueStateSnapshot and get_queue_state.

Tests cover:
- QueueStateSnapshot invariant validation (total = ready + blocked + running + done)
- String formatting (__str__ and to_log_format())
- get_queue_state() with various ticket distributions
- Error handling for overlapping state sets
- Edge cases (empty sets, all blocked, all ready)
"""

from __future__ import annotations

import pytest

from tf.ralph.queue_state import QueueStateSnapshot, get_queue_state


class TestQueueStateSnapshotInvariant:
    """Test QueueStateSnapshot invariant validation."""

    def test_valid_snapshot_succeeds(self):
        """Creating a valid snapshot should succeed."""
        snapshot = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)
        assert snapshot.ready == 3
        assert snapshot.blocked == 2
        assert snapshot.running == 1
        assert snapshot.done == 4
        assert snapshot.total == 10

    def test_zero_counts_succeeds(self):
        """All zeros is a valid state."""
        snapshot = QueueStateSnapshot(ready=0, blocked=0, running=0, done=0, total=0)
        assert snapshot.total == 0

    def test_invariant_violation_raises(self):
        """Mismatched total should raise ValueError."""
        with pytest.raises(ValueError, match="invariant violated"):
            QueueStateSnapshot(ready=1, blocked=1, running=1, done=1, total=10)

    def test_invariant_off_by_one_raises(self):
        """Even off-by-one should raise."""
        with pytest.raises(ValueError, match="invariant violated"):
            QueueStateSnapshot(ready=2, blocked=2, running=1, done=1, total=5)

    def test_invariant_message_includes_counts(self):
        """Error message should include the actual counts."""
        with pytest.raises(ValueError) as exc_info:
            QueueStateSnapshot(ready=1, blocked=2, running=3, done=4, total=100)
        msg = str(exc_info.value)
        assert "ready(1)" in msg
        assert "blocked(2)" in msg
        assert "running(3)" in msg
        assert "done(4)" in msg
        assert "10" in msg  # computed total


class TestQueueStateSnapshotFormatting:
    """Test QueueStateSnapshot string formatting."""

    def test_str_format(self):
        """__str__ should format as 'R:X B:Y (done Z/W)'."""
        snapshot = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)
        assert str(snapshot) == "R:3 B:2 (done 4/10)"

    def test_str_format_zero_counts(self):
        """__str__ should handle zeros correctly."""
        snapshot = QueueStateSnapshot(ready=0, blocked=0, running=0, done=0, total=0)
        assert str(snapshot) == "R:0 B:0 (done 0/0)"

    def test_str_format_single_counts(self):
        """__str__ should handle single-digit counts."""
        snapshot = QueueStateSnapshot(ready=1, blocked=1, running=1, done=1, total=4)
        assert str(snapshot) == "R:1 B:1 (done 1/4)"

    def test_to_log_format(self):
        """to_log_format should format as 'R:X B:Y done:Z/W'."""
        snapshot = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)
        assert snapshot.to_log_format() == "R:3 B:2 done:4/10"

    def test_to_log_format_zero_counts(self):
        """to_log_format should handle zeros correctly."""
        snapshot = QueueStateSnapshot(ready=0, blocked=0, running=0, done=0, total=0)
        assert snapshot.to_log_format() == "R:0 B:0 done:0/0"

    def test_to_log_format_large_counts(self):
        """to_log_format should handle large counts."""
        snapshot = QueueStateSnapshot(
            ready=100, blocked=50, running=25, done=75, total=250
        )
        assert snapshot.to_log_format() == "R:100 B:50 done:75/250"


class TestGetQueueStateBasic:
    """Test get_queue_state basic functionality."""

    def test_empty_sets(self):
        """All empty sets should produce zero snapshot."""
        snapshot = get_queue_state(
            pending=set(),
            running=set(),
            completed=set(),
            dep_graph={},
        )
        assert snapshot.ready == 0
        assert snapshot.blocked == 0
        assert snapshot.running == 0
        assert snapshot.done == 0
        assert snapshot.total == 0

    def test_all_ready_no_deps(self):
        """Pending tickets with no deps should all be ready."""
        snapshot = get_queue_state(
            pending={"T-1", "T-2", "T-3"},
            running=set(),
            completed=set(),
            dep_graph={},
        )
        assert snapshot.ready == 3
        assert snapshot.blocked == 0
        assert snapshot.running == 0
        assert snapshot.done == 0
        assert snapshot.total == 3

    def test_all_blocked(self):
        """All pending tickets blocked by deps."""
        snapshot = get_queue_state(
            pending={"T-1", "T-2"},
            running=set(),
            completed=set(),
            dep_graph={"T-1": {"T-3"}, "T-2": {"T-3"}},
        )
        assert snapshot.ready == 0
        assert snapshot.blocked == 2
        assert snapshot.running == 0
        assert snapshot.done == 0
        assert snapshot.total == 2

    def test_mixed_ready_and_blocked(self):
        """Some ready, some blocked."""
        snapshot = get_queue_state(
            pending={"T-1", "T-2", "T-3"},
            running=set(),
            completed=set(),
            dep_graph={"T-2": {"T-1"}},  # Only T-2 is blocked
        )
        assert snapshot.ready == 2  # T-1 and T-3
        assert snapshot.blocked == 1  # T-2
        assert snapshot.running == 0
        assert snapshot.done == 0
        assert snapshot.total == 3

    def test_with_running(self):
        """Running tickets should be counted."""
        snapshot = get_queue_state(
            pending={"T-1"},
            running={"T-2"},
            completed=set(),
            dep_graph={},
        )
        assert snapshot.ready == 1
        assert snapshot.blocked == 0
        assert snapshot.running == 1
        assert snapshot.done == 0
        assert snapshot.total == 2

    def test_with_completed(self):
        """Completed tickets should be counted."""
        snapshot = get_queue_state(
            pending={"T-1"},
            running=set(),
            completed={"T-2", "T-3"},
            dep_graph={},
        )
        assert snapshot.ready == 1
        assert snapshot.blocked == 0
        assert snapshot.running == 0
        assert snapshot.done == 2
        assert snapshot.total == 3

    def test_full_mix(self):
        """Ready, blocked, running, and done all present."""
        snapshot = get_queue_state(
            pending={"T-1", "T-2", "T-3", "T-4"},
            running={"T-5"},
            completed={"T-6", "T-7"},
            dep_graph={"T-2": {"T-1"}, "T-4": {"T-3"}},  # T-2 and T-4 blocked
        )
        assert snapshot.ready == 2  # T-1 and T-3
        assert snapshot.blocked == 2  # T-2 and T-4
        assert snapshot.running == 1  # T-5
        assert snapshot.done == 2  # T-6 and T-7
        assert snapshot.total == 7


class TestGetQueueStateValidation:
    """Test get_queue_state input validation."""

    def test_pending_and_running_overlap_raises(self):
        """Ticket cannot be both pending and running."""
        with pytest.raises(ValueError, match="cannot be both pending and running"):
            get_queue_state(
                pending={"T-1"},
                running={"T-1"},
                completed=set(),
                dep_graph={},
            )

    def test_pending_and_completed_overlap_raises(self):
        """Ticket cannot be both pending and completed."""
        with pytest.raises(ValueError, match="cannot be both pending and completed"):
            get_queue_state(
                pending={"T-1"},
                running=set(),
                completed={"T-1"},
                dep_graph={},
            )

    def test_running_and_completed_overlap_raises(self):
        """Ticket cannot be both running and completed."""
        with pytest.raises(ValueError, match="cannot be both running and completed"):
            get_queue_state(
                pending=set(),
                running={"T-1"},
                completed={"T-1"},
                dep_graph={},
            )

    def test_triple_overlap_raises(self):
        """Ticket in all three sets should raise on first check."""
        with pytest.raises(ValueError, match="cannot be both pending and running"):
            get_queue_state(
                pending={"T-1"},
                running={"T-1"},
                completed={"T-1"},
                dep_graph={},
            )

    def test_partial_overlap_pending_running(self):
        """Partial overlap should raise."""
        with pytest.raises(ValueError, match="cannot be both pending and running"):
            get_queue_state(
                pending={"T-1", "T-2"},
                running={"T-2", "T-3"},
                completed=set(),
                dep_graph={},
            )

    def test_error_includes_offending_tickets(self):
        """Error message should include the overlapping ticket IDs."""
        with pytest.raises(ValueError) as exc_info:
            get_queue_state(
                pending={"T-1", "T-2"},
                running={"T-2", "T-3"},
                completed=set(),
                dep_graph={},
            )
        assert "T-2" in str(exc_info.value)


class TestGetQueueStateDepGraphEdgeCases:
    """Test edge cases in dependency graph handling."""

    def test_empty_dep_in_dep_graph(self):
        """Empty dep set in dep_graph should not block."""
        snapshot = get_queue_state(
            pending={"T-1", "T-2"},
            running=set(),
            completed=set(),
            dep_graph={"T-1": set()},  # Empty deps = not blocked
        )
        assert snapshot.ready == 2
        assert snapshot.blocked == 0

    def test_pending_ticket_not_in_dep_graph(self):
        """Pending ticket not in dep_graph should be ready."""
        snapshot = get_queue_state(
            pending={"T-1", "T-2"},
            running=set(),
            completed=set(),
            dep_graph={"T-3": {"T-4"}},  # T-3 not in pending
        )
        assert snapshot.ready == 2
        assert snapshot.blocked == 0

    def test_dep_graph_has_running_ticket(self):
        """Dep graph may reference non-pending tickets."""
        snapshot = get_queue_state(
            pending={"T-1"},
            running={"T-2"},
            completed=set(),
            dep_graph={"T-1": {"T-2"}},  # T-2 is running, T-1 blocked
        )
        assert snapshot.ready == 0
        assert snapshot.blocked == 1

    def test_dep_graph_has_completed_ticket(self):
        """Dep graph referencing completed should still block."""
        snapshot = get_queue_state(
            pending={"T-1"},
            running=set(),
            completed={"T-2"},
            dep_graph={"T-1": {"T-2"}},
        )
        # T-1 is still blocked because dep_graph says it has unmet deps
        # (The caller is responsible for updating dep_graph as tickets complete)
        assert snapshot.ready == 0
        assert snapshot.blocked == 1


class TestGetQueueStateFromScheduler:
    """Test get_queue_state_from_scheduler convenience wrapper."""

    def test_with_dep_resolver(self):
        """Using a dependency resolver function."""
        from tf.ralph.queue_state import get_queue_state_from_scheduler

        def resolver(ticket_id: str) -> set[str]:
            deps = {"T-1": {"T-0"}, "T-2": set()}
            return deps.get(ticket_id, set())

        snapshot = get_queue_state_from_scheduler(
            pending={"T-1", "T-2"},
            running=set(),
            completed=set(),
            dep_resolver=resolver,
        )
        assert snapshot.ready == 1  # T-2
        assert snapshot.blocked == 1  # T-1

    def test_without_dep_resolver(self):
        """Without resolver, assumes no dependencies."""
        from tf.ralph.queue_state import get_queue_state_from_scheduler

        snapshot = get_queue_state_from_scheduler(
            pending={"T-1", "T-2"},
            running=set(),
            completed=set(),
            dep_resolver=None,
        )
        assert snapshot.ready == 2
        assert snapshot.blocked == 0

    def test_with_running_and_completed(self):
        """Resolver works with running and completed tickets."""
        from tf.ralph.queue_state import get_queue_state_from_scheduler

        def resolver(ticket_id: str) -> set[str]:
            return {"T-0"} if ticket_id == "T-3" else set()

        snapshot = get_queue_state_from_scheduler(
            pending={"T-3", "T-4"},
            running={"T-5"},
            completed={"T-6"},
            dep_resolver=resolver,
        )
        assert snapshot.ready == 1  # T-4
        assert snapshot.blocked == 1  # T-3
        assert snapshot.running == 1  # T-5
        assert snapshot.done == 1  # T-6
        assert snapshot.total == 4


class TestQueueStateSnapshotImmutability:
    """Test that QueueStateSnapshot is immutable (frozen dataclass)."""

    def test_cannot_modify_ready(self):
        """Cannot modify ready attribute."""
        snapshot = QueueStateSnapshot(ready=1, blocked=0, running=0, done=0, total=1)
        with pytest.raises((AttributeError, TypeError)):
            snapshot.ready = 5

    def test_cannot_modify_blocked(self):
        """Cannot modify blocked attribute."""
        snapshot = QueueStateSnapshot(ready=0, blocked=1, running=0, done=0, total=1)
        with pytest.raises((AttributeError, TypeError)):
            snapshot.blocked = 5

    def test_cannot_modify_running(self):
        """Cannot modify running attribute."""
        snapshot = QueueStateSnapshot(ready=0, blocked=0, running=1, done=0, total=1)
        with pytest.raises((AttributeError, TypeError)):
            snapshot.running = 5

    def test_cannot_modify_done(self):
        """Cannot modify done attribute."""
        snapshot = QueueStateSnapshot(ready=0, blocked=0, running=0, done=1, total=1)
        with pytest.raises((AttributeError, TypeError)):
            snapshot.done = 5

    def test_cannot_modify_total(self):
        """Cannot modify total attribute."""
        snapshot = QueueStateSnapshot(ready=1, blocked=0, running=0, done=0, total=1)
        with pytest.raises((AttributeError, TypeError)):
            snapshot.total = 5
