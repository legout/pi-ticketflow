"""Tests for priority_reclassify command."""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from tf_cli import priority_reclassify_new as pr


class TestParseTicketShow:
    """Test parsing tk show output."""

    def test_parse_basic_ticket(self):
        """Test parsing a basic ticket."""
        output = """---
id: abc-1234
priority: P2
status: open
type: task
tags: [bug, fix]
---
# Fix the bug

Description of the bug fix."""
        
        ticket = pr.parse_ticket_show(output)
        assert ticket["id"] == "abc-1234"
        assert ticket["priority"] == "P2"
        assert ticket["status"] == "open"
        assert ticket["type"] == "task"
        assert ticket["tags"] == ["bug", "fix"]
        assert ticket["title"] == "Fix the bug"
        assert "Description" in ticket["description"]

    def test_parse_closed_ticket(self):
        """Test parsing a closed ticket."""
        output = """---
id: xyz-9999
priority: P3
status: closed
type: task
tags: [docs]
---
# Update documentation"""
        
        ticket = pr.parse_ticket_show(output)
        assert ticket["status"] == "closed"


class TestClassifyPriority:
    """Test priority classification logic."""

    def test_security_keyword_p0(self):
        """Security keywords should classify as P0."""
        ticket = {
            "title": "Fix security vulnerability",
            "description": "",
            "tags": [],
            "type": "bug",
        }
        priority, reason = pr.classify_priority(ticket)
        assert priority == "P0"
        assert "security" in reason.lower() or "critical" in reason.lower()

    def test_crash_keyword_p0(self):
        """Crash keywords should classify as P0."""
        ticket = {
            "title": "App crashes on startup",
            "description": "",
            "tags": [],
            "type": "bug",
        }
        priority, reason = pr.classify_priority(ticket)
        assert priority == "P0"

    def test_blocker_keyword_p1(self):
        """Blocker keywords should classify as P1."""
        ticket = {
            "title": "Blocking release issue",
            "description": "",
            "tags": [],
            "type": "bug",
        }
        priority, reason = pr.classify_priority(ticket)
        assert priority == "P1"

    def test_feature_keyword_p2(self):
        """Feature keywords should classify as P2."""
        ticket = {
            "title": "Add user profile page",
            "description": "",
            "tags": [],
            "type": "feature",
        }
        priority, reason = pr.classify_priority(ticket)
        assert priority == "P2"

    def test_docs_tag_p4(self):
        """Docs tag should classify as P4."""
        ticket = {
            "title": "Update README",
            "description": "",
            "tags": ["docs"],
            "type": "task",
        }
        priority, reason = pr.classify_priority(ticket)
        assert priority == "P4"

    def test_refactor_keyword_p4(self):
        """Refactor keywords should classify as P4."""
        ticket = {
            "title": "Refactor utility functions",
            "description": "",
            "tags": [],
            "type": "task",
        }
        priority, reason = pr.classify_priority(ticket)
        assert priority == "P4"

    def test_performance_keyword_p3(self):
        """Performance keywords should classify as P3."""
        ticket = {
            "title": "Improve query performance",
            "description": "",
            "tags": [],
            "type": "task",
        }
        priority, reason = pr.classify_priority(ticket)
        assert priority == "P3"


class TestFormatPriority:
    """Test priority formatting."""

    def test_format_p0(self):
        assert pr.format_priority("p0") == "P0"
        assert pr.format_priority("P0") == "P0"
        assert pr.format_priority("0") == "P0"

    def test_format_already_formatted(self):
        assert pr.format_priority("P2") == "P2"


class TestGetTicketIds:
    """Test ticket ID collection functions."""

    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_get_ticket_ids_from_ready(self, mock_run):
        """Test getting ready ticket IDs."""
        mock_run.return_value = (0, "abc-1234  Feature description\nxyz-5678  Another feature", "")
        
        ids = pr.get_ticket_ids_from_ready()
        assert "abc-1234" in ids
        assert "xyz-5678" in ids
        mock_run.assert_called_once_with(["ready"])

    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_get_ticket_ids_from_ready_empty(self, mock_run):
        """Test getting ready tickets when none exist."""
        mock_run.return_value = (0, "", "")
        
        ids = pr.get_ticket_ids_from_ready()
        assert ids == []

    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_get_ticket_ids_by_status(self, mock_run):
        """Test getting tickets by status."""
        mock_run.return_value = (0, "abc-1234  open  Feature\nxyz-5678  open  Bug", "")
        
        ids = pr.get_ticket_ids_by_status("open")
        assert "abc-1234" in ids
        mock_run.assert_called_once_with(["ls", "--status", "open"])

    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_get_ticket_ids_by_tag(self, mock_run):
        """Test getting tickets by tag."""
        mock_run.return_value = (0, "abc-1234  open  Feature\nxyz-5678  open  Bug", "")
        
        ids = pr.get_ticket_ids_by_tag("bug")
        assert len(ids) > 0
        mock_run.assert_called_once_with(["ls", "--tag", "bug"])


class TestMainArgumentParsing:
    """Test main argument parsing and validation."""

    @patch("shutil.which")
    def test_no_tk_available(self, mock_which):
        """Test error when tk is not available."""
        mock_which.return_value = None
        
        result = pr.main(["--ids", "abc-1234"])
        assert result == 1

    @patch("shutil.which")
    def test_no_project_found(self, mock_which):
        """Test error when no project found."""
        mock_which.return_value = "/usr/bin/tk"
        
        with patch("tf_cli.priority_reclassify_new.find_project_root") as mock_find:
            mock_find.return_value = None
            result = pr.main(["--ids", "abc-1234"])
            assert result == 1

    @patch("shutil.which")
    def test_missing_required_args(self, mock_which):
        """Test error when no ticket selection args provided."""
        mock_which.return_value = "/usr/bin/tk"
        
        with patch("tf_cli.priority_reclassify_new.find_project_root") as mock_find:
            mock_find.return_value = Path("/tmp/project")
            result = pr.main([])
            assert result == 1


class TestClosedTicketHandling:
    """Test closed ticket exclusion/inclusion."""

    @patch("shutil.which")
    @patch("tf_cli.priority_reclassify_new.find_project_root")
    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_closed_tickets_excluded_by_default(
        self, mock_run, mock_find, mock_which, capsys
    ):
        """Test that closed tickets are excluded by default."""
        mock_which.return_value = "/usr/bin/tk"
        mock_find.return_value = Path("/tmp/project")
        
        # Return a closed ticket
        closed_ticket = """---
id: closed-123
priority: P3
status: closed
type: task
tags: []
---
# Closed ticket

Description."""
        mock_run.return_value = (0, closed_ticket, "")
        
        result = pr.main(["--ids", "closed-123"])
        
        # Should return 0 with message that no tickets to process
        assert result == 0
        captured = capsys.readouterr()
        assert "No tickets to process" in captured.out

    @patch("shutil.which")
    @patch("tf_cli.priority_reclassify_new.find_project_root")
    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    @patch("tf_cli.priority_reclassify_new.print_results")
    @patch("tf_cli.priority_reclassify_new.write_audit_trail")
    def test_closed_tickets_included_with_flag(
        self, mock_audit, mock_print, mock_run, mock_find, mock_which
    ):
        """Test that closed tickets are included with --include-closed."""
        mock_which.return_value = "/usr/bin/tk"
        mock_find.return_value = Path("/tmp/project")
        
        # Return a closed ticket
        closed_ticket = """---
id: closed-123
priority: P3
status: closed
type: task
tags: [docs]
---
# Closed ticket

Description."""
        mock_run.return_value = (0, closed_ticket, "")
        
        result = pr.main(["--ids", "closed-123", "--include-closed"])
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert len(call_args) == 1  # Closed ticket should be processed
        assert call_args[0]["id"] == "closed-123"


class TestTicketSelection:
    """Test ticket selection methods."""

    @patch("shutil.which")
    @patch("tf_cli.priority_reclassify_new.find_project_root")
    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_explicit_ids(self, mock_run, mock_find, mock_which):
        """Test selecting tickets by explicit IDs."""
        mock_which.return_value = "/usr/bin/tk"
        mock_find.return_value = Path("/tmp/project")
        
        ticket_output = """---
id: abc-1234
priority: P2
status: open
type: task
tags: []
---
# Test ticket"""
        mock_run.return_value = (0, ticket_output, "")
        
        with patch("tf_cli.priority_reclassify_new.print_results") as mock_print:
            with patch("tf_cli.priority_reclassify_new.write_audit_trail"):
                pr.main(["--ids", "abc-1234,def-5678"])
                
                # Should call tk show for each ID
                assert mock_run.call_count == 2
                mock_run.assert_any_call(["show", "abc-1234"])
                mock_run.assert_any_call(["show", "def-5678"])

    @patch("shutil.which")
    @patch("tf_cli.priority_reclassify_new.find_project_root")
    @patch("tf_cli.priority_reclassify_new.get_ticket_ids_from_ready")
    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_ready_flag(self, mock_run, mock_ready, mock_find, mock_which):
        """Test selecting tickets with --ready."""
        mock_which.return_value = "/usr/bin/tk"
        mock_find.return_value = Path("/tmp/project")
        mock_ready.return_value = ["ready-1", "ready-2"]
        
        ticket_output = """---
id: ready-1
priority: P2
status: open
type: task
tags: []
---
# Ready ticket"""
        mock_run.return_value = (0, ticket_output, "")
        
        with patch("tf_cli.priority_reclassify_new.print_results") as mock_print:
            with patch("tf_cli.priority_reclassify_new.write_audit_trail"):
                pr.main(["--ready"])
                
                mock_ready.assert_called_once()
                assert mock_run.call_count == 2

    @patch("shutil.which")
    @patch("tf_cli.priority_reclassify_new.find_project_root")
    @patch("tf_cli.priority_reclassify_new.get_ticket_ids_by_status")
    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_status_filter(self, mock_run, mock_status, mock_find, mock_which):
        """Test selecting tickets by status."""
        mock_which.return_value = "/usr/bin/tk"
        mock_find.return_value = Path("/tmp/project")
        mock_status.return_value = ["open-1"]
        
        ticket_output = """---
id: open-1
priority: P2
status: open
type: task
tags: []
---
# Open ticket"""
        mock_run.return_value = (0, ticket_output, "")
        
        with patch("tf_cli.priority_reclassify_new.print_results") as mock_print:
            with patch("tf_cli.priority_reclassify_new.write_audit_trail"):
                pr.main(["--status", "open"])
                
                mock_status.assert_called_once_with("open")

    @patch("shutil.which")
    @patch("tf_cli.priority_reclassify_new.find_project_root")
    @patch("tf_cli.priority_reclassify_new.get_ticket_ids_by_tag")
    @patch("tf_cli.priority_reclassify_new.run_tk_command")
    def test_tag_filter(self, mock_run, mock_tag, mock_find, mock_which):
        """Test selecting tickets by tag."""
        mock_which.return_value = "/usr/bin/tk"
        mock_find.return_value = Path("/tmp/project")
        mock_tag.return_value = ["bug-1"]
        
        ticket_output = """---
id: bug-1
priority: P1
status: open
type: bug
tags: [bug]
---
# Bug ticket"""
        mock_run.return_value = (0, ticket_output, "")
        
        with patch("tf_cli.priority_reclassify_new.print_results") as mock_print:
            with patch("tf_cli.priority_reclassify_new.write_audit_trail"):
                pr.main(["--tag", "bug"])
                
                mock_tag.assert_called_once_with("bug")


class TestAuditTrail:
    """Test audit trail writing."""

    def test_write_audit_trail(self, tmp_path):
        """Test writing audit trail file."""
        results = [
            {
                "id": "abc-1234",
                "current": "P2",
                "proposed": "P1",
                "reason": "Bug fix",
            },
            {
                "id": "xyz-5678",
                "current": "P3",
                "proposed": "P3",
                "reason": "No change",
            },
        ]
        
        pr.write_audit_trail(tmp_path, results, apply=False)
        
        # Check that audit file was created
        knowledge_dir = tmp_path / ".tf" / "knowledge"
        audit_files = list(knowledge_dir.glob("priority-reclassify-*.md"))
        assert len(audit_files) == 1
        
        content = audit_files[0].read_text()
        assert "abc-1234" in content
        assert "xyz-5678" in content
        assert "DRY RUN" in content


class TestIntegration:
    """Integration tests requiring actual tk."""

    @pytest.mark.skipif(
        subprocess.run(["which", "tk"], capture_output=True).returncode != 0,
        reason="tk not available"
    )
    def test_help_output(self):
        """Test that help includes all selection options."""
        result = subprocess.run(
            ["python", "-m", "tf_cli.priority_reclassify_new", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--ids" in result.stdout
        assert "--ready" in result.stdout
        assert "--status" in result.stdout
        assert "--tag" in result.stdout
        assert "--include-closed" in result.stdout
        assert "--apply" in result.stdout