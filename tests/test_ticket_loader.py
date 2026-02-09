"""Tests for the ticket loader in tf/ticket_loader.py."""

import pytest
from pathlib import Path

from tf.ticket_loader import (
    Ticket,
    TicketLoader,
    TicketLoadError,
    format_ticket_list,
    FRONTMATTER_PATTERN,
    TITLE_PATTERN,
)


class TestFrontmatterPattern:
    """Tests for the frontmatter regex pattern."""

    def test_basic_frontmatter(self):
        content = "---\nid: pt-test\nstatus: open\n---\n# Title\nBody"
        match = FRONTMATTER_PATTERN.match(content)
        assert match is not None
        assert match.group(1) == "id: pt-test\nstatus: open"
        assert match.group(2) == "# Title\nBody"

    def test_windows_line_endings(self):
        """Test that Windows CRLF line endings are handled."""
        content = "---\r\nid: pt-test\r\nstatus: open\r\n---\r\n# Title\r\nBody"
        match = FRONTMATTER_PATTERN.match(content)
        assert match is not None
        assert "id: pt-test" in match.group(1)
        assert "# Title" in match.group(2)

    def test_no_frontmatter(self):
        content = "# Title\nBody"
        match = FRONTMATTER_PATTERN.match(content)
        assert match is None

    def test_empty_frontmatter(self):
        # Empty frontmatter (no content between markers) is technically valid
        content = "---\n---\n# Title\nBody"
        match = FRONTMATTER_PATTERN.match(content)
        # Our pattern requires at least one character between markers
        # So this won't match - that's acceptable behavior
        assert match is None


class TestTitlePattern:
    """Tests for the title regex pattern."""

    def test_basic_title(self):
        content = "# My Title\nSome body"
        match = TITLE_PATTERN.search(content)
        assert match is not None
        assert match.group(1) == "My Title"

    def test_title_with_extra_spaces(self):
        content = "#   Spaced Title  \nBody"
        match = TITLE_PATTERN.search(content)
        assert match is not None
        # Leading whitespace is consumed by \s*, trailing is preserved
        assert match.group(1) == "Spaced Title  "

    def test_no_title(self):
        content = "Some body without heading"
        match = TITLE_PATTERN.search(content)
        assert match is None

    def test_title_with_hash_in_body(self):
        content = "# Real Title\n## Subheading"
        match = TITLE_PATTERN.search(content)
        assert match is not None
        assert match.group(1) == "Real Title"


class TestTicket:
    """Tests for the Ticket dataclass."""

    def test_basic_creation(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\n# Test Title\nBody content")

        ticket = Ticket(
            id="pt-test",
            status="open",
            title="Test Title",
            file_path=ticket_file,
        )
        assert ticket.id == "pt-test"
        assert ticket.status == "open"
        assert ticket.title == "Test Title"
        assert ticket._body is None
        assert ticket._body_loaded is False

    def test_lazy_body_loading(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\n# Test Title\n\nBody paragraph 1\n\nBody paragraph 2")

        ticket = Ticket(
            id="pt-test",
            status="open",
            title="Test Title",
            file_path=ticket_file,
        )

        # Body not loaded yet
        assert ticket._body_loaded is False

        # Access triggers lazy load
        body = ticket.body
        assert ticket._body_loaded is True
        assert "Body paragraph 1" in body
        assert "# Test Title" not in body  # Title should be stripped

    def test_body_without_title(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\nBody without title heading")

        ticket = Ticket(
            id="pt-test",
            status="open",
            title="",
            file_path=ticket_file,
        )

        body = ticket.body
        assert "Body without title heading" in body

    def test_body_file_not_found(self, tmp_path):
        nonexistent_file = tmp_path / "does-not-exist.md"

        ticket = Ticket(
            id="pt-test",
            status="open",
            title="Test",
            file_path=nonexistent_file,
        )

        body = ticket.body
        assert body == ""
        assert ticket._body_loaded is True

    def test_get_summary_basic(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\n# Title")

        ticket = Ticket(
            id="pt-test",
            status="open",
            title="Test Title",
            file_path=ticket_file,
        )

        summary = ticket.get_summary()
        assert "[open] pt-test: Test Title" in summary

    def test_get_summary_with_metadata(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\n# Title")

        ticket = Ticket(
            id="pt-test",
            status="in-progress",
            title="Test Title",
            file_path=ticket_file,
            assignee="legout",
            tags=["tf", "bug"],
            deps=["pt-123", "pt-456"],
        )

        summary = ticket.get_summary()
        assert "[in-progress] pt-test: Test Title" in summary
        assert "Assignee: legout" in summary
        assert "Tags: tf, bug" in summary
        assert "Dependencies: pt-123, pt-456" in summary


class TestTicketLoader:
    """Tests for the TicketLoader class."""

    @pytest.fixture
    def tmp_tickets_dir(self, tmp_path):
        """Create a temporary tickets directory with sample tickets."""
        tickets_dir = tmp_path / ".tickets"
        tickets_dir.mkdir()

        # Valid open ticket
        (tickets_dir / "pt-open1.md").write_text(
            "---\n"
            "id: pt-open1\n"
            "status: open\n"
            "deps: [pt-dep1]\n"
            "tags: [tf, bug]\n"
            "assignee: legout\n"
            "external-ref: plan-test\n"
            "priority: 2\n"
            "type: task\n"
            "created: 2026-02-08T17:59:15Z\n"
            "links: [pt-link1]\n"
            "---\n"
            "# Open Ticket 1\n"
            "\n"
            "Description of the open ticket.\n"
        )

        # Valid closed ticket
        (tickets_dir / "pt-closed1.md").write_text(
            "---\n"
            "id: pt-closed1\n"
            "status: closed\n"
            "tags: [feature]\n"
            "assignee: someone\n"
            "---\n"
            "# Closed Ticket 1\n"
            "\n"
            "Description of closed ticket.\n"
        )

        # Ticket with no frontmatter (malformed)
        (tickets_dir / "pt-malformed.md").write_text(
            "# No Frontmatter\nThis ticket has no frontmatter"
        )

        # Empty file (malformed)
        (tickets_dir / "pt-empty.md").write_text("")

        return tickets_dir

    def test_load_all_success(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        tickets = loader.load_all()

        # Should load valid tickets, skip malformed ones
        assert len(tickets) == 2
        ids = {t.id for t in tickets}
        assert ids == {"pt-open1", "pt-closed1"}

    def test_tickets_dir_not_found(self, tmp_path):
        nonexistent = tmp_path / "does-not-exist"
        loader = TicketLoader(nonexistent)

        with pytest.raises(TicketLoadError, match="not found"):
            loader.load_all()

    def test_get_by_id(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        ticket = loader.get_by_id("pt-open1")
        assert ticket is not None
        assert ticket.id == "pt-open1"
        assert ticket.status == "open"

        missing = loader.get_by_id("pt-nonexistent")
        assert missing is None

    def test_get_by_id_not_loaded(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)

        with pytest.raises(TicketLoadError, match="not loaded"):
            loader.get_by_id("pt-open1")

    def test_get_by_status(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        open_tickets = loader.get_by_status("open")
        assert len(open_tickets) == 1
        assert open_tickets[0].id == "pt-open1"

        closed_tickets = loader.get_by_status("closed")
        assert len(closed_tickets) == 1
        assert closed_tickets[0].id == "pt-closed1"

        unknown_tickets = loader.get_by_status("unknown")
        assert len(unknown_tickets) == 0

    def test_get_by_tag(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        tf_tickets = loader.get_by_tag("tf")
        assert len(tf_tickets) == 1
        assert tf_tickets[0].id == "pt-open1"

        bug_tickets = loader.get_by_tag("bug")
        assert len(bug_tickets) == 1

        feature_tickets = loader.get_by_tag("feature")
        assert len(feature_tickets) == 1

        nonexistent_tickets = loader.get_by_tag("nonexistent")
        assert len(nonexistent_tickets) == 0

    def test_get_by_assignee(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        legout_tickets = loader.get_by_assignee("legout")
        assert len(legout_tickets) == 1
        assert legout_tickets[0].id == "pt-open1"

        someone_tickets = loader.get_by_assignee("someone")
        assert len(someone_tickets) == 1

        noone_tickets = loader.get_by_assignee("noone")
        assert len(noone_tickets) == 0

    def test_search_by_id(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        results = loader.search("pt-open")
        assert len(results) == 1
        assert results[0].id == "pt-open1"

    def test_search_by_title(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        results = loader.search("Open Ticket")
        assert len(results) == 1
        assert results[0].id == "pt-open1"

    def test_search_by_tag(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        results = loader.search("feature")
        assert len(results) == 1
        assert results[0].id == "pt-closed1"

    def test_search_case_insensitive(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        results_lower = loader.search("open")
        results_upper = loader.search("OPEN")
        results_mixed = loader.search("Open")

        assert len(results_lower) == len(results_upper) == len(results_mixed)

    def test_all_tickets_property(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        tickets = loader.all_tickets
        assert len(tickets) == 2

        # Should return a copy
        tickets.pop()
        assert len(loader.all_tickets) == 2

    def test_count_by_status(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        counts = loader.count_by_status
        assert counts["open"] == 1
        assert counts["closed"] == 1

    def test_count_by_status_not_loaded(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)

        counts = loader.count_by_status
        assert counts == {}

    def test_parses_all_fields(self, tmp_tickets_dir):
        loader = TicketLoader(tmp_tickets_dir)
        loader.load_all()

        ticket = loader.get_by_id("pt-open1")
        assert ticket.id == "pt-open1"
        assert ticket.status == "open"
        assert ticket.title == "Open Ticket 1"
        assert ticket.deps == ["pt-dep1"]
        assert ticket.tags == ["tf", "bug"]
        assert ticket.assignee == "legout"
        assert ticket.external_ref == "plan-test"
        assert ticket.priority == 2
        assert ticket.ticket_type == "task"
        # YAML may parse timestamp as datetime or string depending on implementation
        assert ticket.created is not None
        assert ticket.links == ["pt-link1"]

    def test_resolve_tickets_dir_from_cwd(self, tmp_path, monkeypatch):
        """Test that tickets dir resolves from cwd when no repo root found."""
        monkeypatch.chdir(tmp_path)
        tickets_dir = tmp_path / ".tickets"
        tickets_dir.mkdir()
        (tickets_dir / "pt-test.md").write_text(
            "---\nid: pt-test\nstatus: open\n---\n# Test"
        )

        loader = TicketLoader()  # No path provided
        tickets = loader.load_all()
        assert len(tickets) == 1

    def test_resolve_tickets_dir_from_repo_root(self, tmp_path, monkeypatch):
        """Test that tickets dir resolves from repo root when .tf exists."""
        # Create repo structure
        tf_dir = tmp_path / ".tf"
        tf_dir.mkdir()
        tickets_dir = tmp_path / ".tickets"
        tickets_dir.mkdir()
        (tickets_dir / "pt-test.md").write_text(
            "---\nid: pt-test\nstatus: open\n---\n# Test"
        )

        # Change to a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        loader = TicketLoader()
        tickets = loader.load_all()
        assert len(tickets) == 1


class TestBasicFrontmatterParsing:
    """Tests for the basic frontmatter parser (YAML fallback)."""

    def test_parse_simple_fields(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "id: pt-test\nstatus: open\nassignee: legout"
        result = loader._basic_parse_frontmatter(text)

        assert result["id"] == "pt-test"
        assert result["status"] == "open"
        assert result["assignee"] == "legout"

    def test_parse_list_field(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = 'deps: [pt-1, pt-2, pt-3]\ntags: [bug, tf]'
        result = loader._basic_parse_frontmatter(text)

        assert result["deps"] == ["pt-1", "pt-2", "pt-3"]
        assert result["tags"] == ["bug", "tf"]

    def test_parse_integer_field(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "priority: 2\ncount: 42"
        result = loader._basic_parse_frontmatter(text)

        assert result["priority"] == 2
        assert result["count"] == 42

    def test_parse_negative_integer(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "offset: -5"
        result = loader._basic_parse_frontmatter(text)

        assert result["offset"] == -5

    def test_parse_float_field(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "progress: 0.75\nvalue: 3.14"
        result = loader._basic_parse_frontmatter(text)

        assert result["progress"] == 0.75
        assert result["value"] == 3.14

    def test_parse_boolean_fields(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "active: true\narchived: false"
        result = loader._basic_parse_frontmatter(text)

        assert result["active"] is True
        assert result["archived"] is False

    def test_parse_empty_value(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "optional:"
        result = loader._basic_parse_frontmatter(text)

        assert result["optional"] is None

    def test_skips_comments(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "# This is a comment\nid: pt-test"
        result = loader._basic_parse_frontmatter(text)

        assert "# This is a comment" not in result
        assert result["id"] == "pt-test"

    def test_skips_empty_lines(self, tmp_path):
        loader = TicketLoader(tmp_path)
        text = "id: pt-test\n\nstatus: open"
        result = loader._basic_parse_frontmatter(text)

        assert result["id"] == "pt-test"
        assert result["status"] == "open"


class TestFormatTicketList:
    """Tests for format_ticket_list function."""

    def test_empty_list(self):
        result = format_ticket_list([])
        assert result == "No tickets found."

    def test_single_ticket(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\n# Title")

        ticket = Ticket(id="pt-test", status="open", title="Test Ticket", file_path=ticket_file)
        result = format_ticket_list([ticket])

        assert "pt-test" in result
        assert "Test Ticket" in result
        assert "[open]" in result

    def test_multiple_tickets(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\n# Title")

        tickets = [
            Ticket(id="pt-1", status="open", title="First", file_path=ticket_file),
            Ticket(id="pt-2", status="closed", title="Second", file_path=ticket_file),
        ]
        result = format_ticket_list(tickets)
        lines = result.strip().split("\n")

        assert len(lines) == 2
        assert "First" in lines[0]
        assert "Second" in lines[1]

    def test_with_tags(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text("---\nid: pt-test\n---\n# Title")

        ticket = Ticket(
            id="pt-test",
            status="open",
            title="Test",
            file_path=ticket_file,
            tags=["tf", "bug"],
        )
        result = format_ticket_list([ticket], show_tags=True)

        assert "tf" in result
        assert "bug" in result


class TestTicketBodyLoading:
    """Tests for lazy body loading functionality."""

    def test_body_strips_frontmatter(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text(
            "---\n"
            "id: pt-test\n"
            "status: open\n"
            "---\n"
            "# Title\n"
            "\n"
            "This is the body.\n"
        )

        ticket = Ticket(id="pt-test", status="open", title="Title", file_path=ticket_file)
        body = ticket.body

        assert "---" not in body
        assert "id: pt-test" not in body
        assert "This is the body." in body

    def test_body_strips_title(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text(
            "---\n"
            "id: pt-test\n"
            "---\n"
            "# The Title\n"
            "\n"
            "Body content here.\n"
        )

        ticket = Ticket(id="pt-test", status="open", title="The Title", file_path=ticket_file)
        body = ticket.body

        assert "# The Title" not in body
        assert "Body content here." in body

    def test_body_preserved_whitespace(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text(
            "---\n"
            "id: pt-test\n"
            "---\n"
            "# Title\n"
            "\n"
            "Paragraph 1\n"
            "\n"
            "Paragraph 2\n"
        )

        ticket = Ticket(id="pt-test", status="open", title="Title", file_path=ticket_file)
        body = ticket.body

        assert "Paragraph 1" in body
        assert "Paragraph 2" in body

    def test_body_with_subheadings(self, tmp_path):
        ticket_file = tmp_path / "pt-test.md"
        ticket_file.write_text(
            "---\n"
            "id: pt-test\n"
            "---\n"
            "# Main Title\n"
            "\n"
            "Intro\n"
            "\n"
            "## Section 1\n"
            "Content 1\n"
            "\n"
            "## Section 2\n"
            "Content 2\n"
        )

        ticket = Ticket(id="pt-test", status="open", title="Main Title", file_path=ticket_file)
        body = ticket.body

        # Should keep subheadings but not main title
        assert "# Main Title" not in body
        assert "## Section 1" in body
        assert "## Section 2" in body
        assert "Content 1" in body
