"""Integration tests for RalphLogger with QueueStateSnapshot.

Tests cover:
- Log lines include R: and B: counts
- Both start and complete log formats
- to_log_format() output in log messages
"""

from __future__ import annotations

import io
import re

import pytest

from tf.logger import LogLevel, RalphLogger, create_logger
from tf.ralph.queue_state import QueueStateSnapshot


class TestLoggerTicketStartWithQueueState:
    """Test log_ticket_start with queue state."""

    def test_ticket_start_includes_queue_state(self):
        """log_ticket_start should include queue state in message."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        logger.log_ticket_start("pt-abc123", mode="serial", iteration=1, queue_state=queue_state)

        content = output.getvalue()
        # Should contain the queue state in log format
        assert "R:3 B:2 done:4/10" in content
        assert "Starting ticket processing: pt-abc123" in content

    def test_ticket_start_with_zero_queue_state(self):
        """log_ticket_start with zero counts should display correctly."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=0, blocked=0, running=0, done=0, total=0)

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert "R:0 B:0 done:0/0" in content

    def test_ticket_start_without_queue_state(self):
        """log_ticket_start without queue_state should omit it."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)

        logger.log_ticket_start("pt-abc123", mode="serial", iteration=1)

        content = output.getvalue()
        # Should NOT contain R: or B: or done:
        assert "R:" not in content
        assert "B:" not in content
        assert "done:" not in content
        # But should still have the message
        assert "Starting ticket processing: pt-abc123" in content

    def test_ticket_start_with_large_queue_state(self):
        """log_ticket_start should handle large numbers."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(
            ready=100, blocked=50, running=25, done=75, total=250
        )

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert "R:100 B:50 done:75/250" in content


class TestLoggerTicketCompleteWithQueueState:
    """Test log_ticket_complete with queue state."""

    def test_ticket_complete_success_includes_queue_state(self):
        """log_ticket_complete with COMPLETE should include queue state."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=2, blocked=1, running=1, done=5, total=9)

        logger.log_ticket_complete(
            "pt-abc123", "COMPLETE", mode="serial", iteration=1, queue_state=queue_state
        )

        content = output.getvalue()
        assert "R:2 B:1 done:5/9" in content
        assert "Ticket processing complete: pt-abc123" in content
        assert "INFO" in content  # Success is INFO level

    def test_ticket_complete_failure_includes_queue_state(self):
        """log_ticket_complete with FAILED should include queue state."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=1, blocked=2, running=0, done=3, total=6)

        logger.log_ticket_complete(
            "pt-abc123", "FAILED", mode="serial", iteration=1, queue_state=queue_state
        )

        content = output.getvalue()
        assert "R:1 B:2 done:3/6" in content
        assert "Ticket processing failed: pt-abc123" in content
        assert "ERROR" in content  # Failure is ERROR level

    def test_ticket_complete_without_queue_state(self):
        """log_ticket_complete without queue_state should omit it."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)

        logger.log_ticket_complete("pt-abc123", "COMPLETE", mode="serial", iteration=1)

        content = output.getvalue()
        # Should NOT contain queue state format
        assert "R:" not in content
        assert "B:" not in content
        assert "done:" not in content


class TestLoggerQueueStateFormatPatterns:
    """Test regex patterns for queue state in log output."""

    def test_r_b_done_pattern_in_start(self):
        """Start log should match R:X B:Y done:Z/W pattern."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        # Stable regex pattern for log format
        assert re.search(r"R:\d+ B:\d+ done:\d+/\d+", content)

    def test_r_b_done_pattern_in_complete(self):
        """Complete log should match R:X B:Y done:Z/W pattern."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        logger.log_ticket_complete("pt-abc123", "COMPLETE", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert re.search(r"R:\d+ B:\d+ done:\d+/\d+", content)

    def test_queue_state_in_context_field(self):
        """Queue state should appear as a context field in logs."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.DEBUG, output=output)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        # In DEBUG level, context fields should be visible
        # queue_state is stored as str(queue_state) which renders as "R:3 B:2 (done 4/10)"
        assert "queue_state=" in content
        assert "R:3 B:2 (done 4/10)" in content


class TestLoggerQueueStateWithTicketTitle:
    """Test queue state combined with ticket title."""

    def test_ticket_start_with_title_and_queue_state(self):
        """Both ticket_title and queue_state should appear in start log."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.DEBUG, output=output)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        logger.log_ticket_start(
            ticket_id="pt-abc123",
            ticket_title="Fix authentication bug",
            mode="serial",
            iteration=1,
            queue_state=queue_state,
        )

        content = output.getvalue()
        assert "pt-abc123" in content
        assert "Fix authentication bug" in content
        assert "R:3 B:2 done:4/10" in content

    def test_ticket_complete_with_title_and_queue_state(self):
        """Both ticket_title and queue_state should appear in complete log."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.DEBUG, output=output)
        queue_state = QueueStateSnapshot(ready=2, blocked=1, running=1, done=5, total=9)

        logger.log_ticket_complete(
            ticket_id="pt-abc123",
            status="COMPLETE",
            ticket_title="Fix authentication bug",
            mode="serial",
            iteration=1,
            queue_state=queue_state,
        )

        content = output.getvalue()
        assert "pt-abc123" in content
        assert "R:2 B:1 done:5/9" in content


class TestLoggerQueueStateWithFactory:
    """Test queue state with create_logger factory."""

    def test_factory_logger_with_queue_state(self):
        """Logger created via factory should handle queue state."""
        output = io.StringIO()
        logger = create_logger(level=LogLevel.INFO, mode="serial", output=output)
        queue_state = QueueStateSnapshot(ready=5, blocked=3, running=1, done=2, total=11)

        logger.log_ticket_start("pt-abc123", queue_state=queue_state)

        content = output.getvalue()
        assert "R:5 B:3 done:2/11" in content


class TestLoggerQueueStateEdgeCases:
    """Test edge cases for queue state logging."""

    def test_all_blocked_queue_state(self):
        """Queue state with all tickets blocked."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=0, blocked=10, running=0, done=0, total=10)

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert "R:0 B:10 done:0/10" in content

    def test_all_ready_queue_state(self):
        """Queue state with all tickets ready."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=10, blocked=0, running=0, done=0, total=10)

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert "R:10 B:0 done:0/10" in content

    def test_all_done_queue_state(self):
        """Queue state with all tickets done."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=0, blocked=0, running=0, done=10, total=10)

        logger.log_ticket_complete("pt-abc123", "COMPLETE", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert "R:0 B:0 done:10/10" in content

    def test_single_ticket_queue_state(self):
        """Queue state with single ticket."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.INFO, output=output)
        queue_state = QueueStateSnapshot(ready=1, blocked=0, running=0, done=0, total=1)

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert "R:1 B:0 done:0/1" in content


class TestLoggerQueueStateLogLevelFiltering:
    """Test queue state logging respects log level."""

    def test_queue_state_not_logged_when_level_too_high(self):
        """Queue state should not appear when log level filters out the message."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.ERROR, output=output)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        # log_ticket_start is INFO level, should be filtered at ERROR level
        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert content == ""  # Nothing logged

    def test_queue_state_logged_at_debug_level(self):
        """Queue state should appear at DEBUG level."""
        output = io.StringIO()
        logger = RalphLogger(level=LogLevel.DEBUG, output=output)
        queue_state = QueueStateSnapshot(ready=3, blocked=2, running=1, done=4, total=10)

        logger.log_ticket_start("pt-abc123", mode="serial", queue_state=queue_state)

        content = output.getvalue()
        assert "R:3 B:2 done:4/10" in content
