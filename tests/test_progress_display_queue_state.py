"""Integration tests for ProgressDisplay with QueueStateSnapshot.

Tests cover:
- Progress display includes R: and B: counts in output
- TTY mode formatting with queue state
- Non-TTY mode formatting with queue state
- Ticket start/finish includes queue state
"""

from __future__ import annotations

import re
from io import StringIO

import pytest

from tf.ralph import ProgressDisplay
from tf.ralph.queue_state import QueueStateSnapshot


# Timestamp pattern: HH:MM:SS (24-hour format)
TIMESTAMP_PATTERN = r"\d{2}:\d{2}:\d{2}"


class TestProgressDisplayWithQueueStateNonTTY:
    """Test ProgressDisplay with queue state in non-TTY mode."""

    def test_start_ticket_accepts_queue_state(self):
        """Non-TTY: start_ticket accepts queue_state param, stores state internally."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        display.start_ticket("abc-123", 0, 10, queue_state=queue_state)

        # In non-TTY mode, start_ticket produces no visible output
        # But we verify the queue_state was accepted and ticket state updated
        assert display.current_ticket == "abc-123"
        assert display.total == 10

    def test_complete_ticket_shows_queue_state(self):
        """Non-TTY: complete_ticket should include queue state in output without control chars."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=2, blocked=1, running=1, done=5, total=9)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        # Should contain the queue state format R:X B:Y (done Z/W)
        assert re.search(r"R:\d+ B:\d+", result)
        assert "(done 5/9)" in result
        # Non-TTY mode: no control characters (AC: readable non-animated output)
        assert "\r" not in result, "Non-TTY output should not contain carriage return"
        assert "\x1b" not in result, "Non-TTY output should not contain ANSI escape sequences"

    def test_complete_ticket_failure_with_queue_state(self):
        """Non-TTY: failed ticket should show queue state."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=1, blocked=2, running=0, done=3, total=6)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "FAILED", 0, queue_state=queue_state)

        result = output.getvalue()
        assert re.search(r"R:\d+ B:\d+", result)
        assert "(done 3/6)" in result

    def test_queue_state_format_in_output(self):
        """Queue state should use correct format R:X B:Y (done Z/W)."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=5, blocked=3, running=1, done=2, total=11)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert "R:5 B:3 (done 2/11)" in result

    def test_zero_queue_state_in_output(self):
        """Queue state with zeros should display correctly."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=0, blocked=0, running=0, done=0, total=0)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert "R:0 B:0 (done 0/0)" in result

    def test_no_queue_state_omits_state(self):
        """Without queue_state, the state string should be omitted."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=None)

        result = output.getvalue()
        # Should NOT contain R: or B:
        assert "R:" not in result
        assert "B:" not in result
        # But should contain the completion message
        assert "abc-123 complete" in result


class TestProgressDisplayWithQueueStateTTY:
    """Test ProgressDisplay with queue state in TTY mode."""

    def test_tty_start_ticket_shows_queue_state(self):
        """TTY: start_ticket should include queue state."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=True)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        display.start_ticket("abc-123", 0, 10, queue_state=queue_state)

        result = output.getvalue()
        # Should contain timestamp and queue state
        assert re.search(TIMESTAMP_PATTERN, result)
        assert "R:3 B:2 (done 4/10)" in result
        assert "Processing abc-123" in result

    def test_tty_complete_ticket_shows_queue_state(self):
        """TTY: complete_ticket should include queue state."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=True)
        queue_state = QueueStateSnapshot(ready=2, blocked=1, running=1, done=5, total=9)

        display.start_ticket("abc-123", 0, 10)
        output.truncate(0)
        output.seek(0)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert "R:2 B:1 (done 5/9)" in result
        assert "abc-123 complete" in result

    def test_tty_queue_state_with_carriage_return(self):
        """TTY: queue state should appear with carriage return handling."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=True)
        queue_state = QueueStateSnapshot(ready=4, blocked=1, running=2, done=3, total=10)

        display.start_ticket("abc-123", 0, 10, queue_state=queue_state)

        result = output.getvalue()
        # TTY mode uses carriage return and escape sequences
        assert "\r" in result
        assert "\x1b[2K" in result  # Clear line sequence
        # Queue state should be present
        assert "R:4 B:1 (done 3/10)" in result


class TestProgressDisplayQueueStateIntegration:
    """Integration tests for ProgressDisplay with queue state."""

    def test_full_sequence_with_queue_state_updates(self):
        """Test a full sequence where queue state updates each ticket."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)

        # Simulate processing 3 tickets with evolving queue state
        states = [
            QueueStateSnapshot(ready=2, blocked=1, running=1, done=0, total=4),  # First ticket
            QueueStateSnapshot(ready=1, blocked=1, running=1, done=1, total=4),  # Second ticket
            QueueStateSnapshot(ready=0, blocked=1, running=1, done=2, total=4),  # Third ticket
        ]

        for i, queue_state in enumerate(states):
            ticket_id = f"ticket-{i + 1}"
            display.start_ticket(ticket_id, i, 4, queue_state=queue_state)
            display.complete_ticket(ticket_id, "COMPLETE", i, queue_state=queue_state)

        result = output.getvalue()
        lines = result.strip().split("\n")

        # Should have 3 completion lines
        assert len(lines) == 3

        # Each line should have queue state
        for line in lines:
            assert re.search(r"R:\d+ B:\d+", line)
            assert re.search(TIMESTAMP_PATTERN, line)

    def test_queue_state_preserves_across_calls(self):
        """Queue state should be passed correctly to each method call."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)

        state1 = QueueStateSnapshot(ready=5, blocked=0, running=1, done=0, total=6)
        state2 = QueueStateSnapshot(ready=4, blocked=0, running=1, done=1, total=6)

        display.start_ticket("ticket-1", 0, 6, queue_state=state1)
        display.complete_ticket("ticket-1", "COMPLETE", 0, queue_state=state1)

        result1 = output.getvalue()
        assert "R:5 B:0 (done 0/6)" in result1

        display.start_ticket("ticket-2", 1, 6, queue_state=state2)
        display.complete_ticket("ticket-2", "COMPLETE", 1, queue_state=state2)

        result2 = output.getvalue()
        assert "R:4 B:0 (done 1/6)" in result2

    def test_large_queue_state_values(self):
        """Queue state should handle large numbers correctly."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(
            ready=100, blocked=50, running=25, done=75, total=250
        )

        display.start_ticket("abc-123", 0, 250)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert "R:100 B:50 (done 75/250)" in result

    def test_all_blocked_queue_state(self):
        """Queue state showing all tickets blocked."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=0, blocked=5, running=0, done=0, total=5)

        display.start_ticket("abc-123", 0, 5)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert "R:0 B:5 (done 0/5)" in result

    def test_all_ready_queue_state(self):
        """Queue state showing all tickets ready."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=5, blocked=0, running=0, done=0, total=5)

        display.start_ticket("abc-123", 0, 5)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert "R:5 B:0 (done 0/5)" in result


class TestProgressDisplayQueueStatePatternMatching:
    """Test regex patterns for stable assertions on queue state output."""

    def test_r_pattern_matches(self):
        """R:X pattern should match ready count."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        # Stable regex pattern
        assert re.search(r"R:\d+", result)
        # Specific value
        assert re.search(r"R:3\b", result)

    def test_b_pattern_matches(self):
        """B:X pattern should match blocked count."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert re.search(r"B:\d+", result)
        assert re.search(r"B:2\b", result)

    def test_done_pattern_matches(self):
        """(done X/Y) pattern should match completion progress."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        assert re.search(r"\(done \d+/\d+\)", result)
        assert "(done 4/10)" in result

    def test_combined_pattern_matches(self):
        """Full queue state pattern should match."""
        output = StringIO()
        display = ProgressDisplay(output=output, is_tty=False)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        display.start_ticket("abc-123", 0, 10)
        display.complete_ticket("abc-123", "COMPLETE", 0, queue_state=queue_state)

        result = output.getvalue()
        # Combined pattern for full state string
        assert re.search(r"R:\d+ B:\d+ \(done \d+/\d+\)", result)
