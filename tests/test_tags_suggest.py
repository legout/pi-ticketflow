"""Tests for tf.tags_suggest module."""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from tf import tags_suggest as tags_module
from tf.component_classifier import ClassificationResult


class TestRunSuggest:
    """Tests for run_suggest function."""

    @patch.object(tags_module, "classify_components")
    def test_suggest_with_title(self, mock_classify: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test tag suggestion with title."""
        mock_classify.return_value = ClassificationResult(
            tags=["component:cli"],
            rationale={"component:cli": "Contains CLI keywords"},
            matched_keywords={"component:cli": ["cli", "command"]}
        )
        
        result = tags_module.run_suggest(
            title="Add new CLI command",
            description="",
            ticket_id=None
        )
        
        assert result == 0
        captured = capsys.readouterr()
        assert "component:cli" in captured.out

    @patch.object(tags_module, "suggest_tags_for_ticket")
    def test_suggest_with_ticket_id(self, mock_suggest: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test tag suggestion with ticket ID."""
        mock_suggest.return_value = ClassificationResult(
            tags=["component:tests"],
            rationale={"component:tests": "Test-related"},
            matched_keywords={"component:tests": ["test"]}
        )
        
        result = tags_module.run_suggest(
            title=None,
            description=None,
            ticket_id="abc-123"
        )
        
        assert result == 0
        mock_suggest.assert_called_once_with("abc-123")

    @patch.object(tags_module, "suggest_tags_for_ticket")
    def test_suggest_handles_ticket_error(self, mock_suggest: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test error handling for invalid ticket."""
        mock_suggest.side_effect = RuntimeError("Ticket not found")
        
        result = tags_module.run_suggest(
            title=None,
            description=None,
            ticket_id="invalid"
        )
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_suggest_requires_title_or_ticket(self, capsys: pytest.CaptureFixture) -> None:
        """Test that either title or ticket is required."""
        result = tags_module.run_suggest(
            title=None,
            description=None,
            ticket_id=None
        )
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    @patch.object(tags_module, "classify_components")
    def test_suggest_json_output(self, mock_classify: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test JSON output format."""
        mock_classify.return_value = ClassificationResult(
            tags=["component:api"],
            rationale={"component:api": "API keywords"},
            matched_keywords={"component:api": ["api", "endpoint"]}
        )
        
        result = tags_module.run_suggest(
            title="API endpoint",
            description="",
            ticket_id=None,
            json_output=True
        )
        
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["tags"] == ["component:api"]
        assert "rationale" in output

    @patch.object(tags_module, "classify_components")
    def test_suggest_with_rationale(self, mock_classify: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test showing rationale."""
        mock_classify.return_value = ClassificationResult(
            tags=["component:docs"],
            rationale={"component:docs": "Documentation keywords"},
            matched_keywords={"component:docs": ["doc", "readme"]}
        )
        
        result = tags_module.run_suggest(
            title="Update docs",
            description="",
            ticket_id=None,
            show_rationale=True
        )
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Rationale:" in captured.out
        assert "component:docs:" in captured.out

    @patch.object(tags_module, "classify_components")
    def test_suggest_no_tags_found(self, mock_classify: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test output when no tags match."""
        mock_classify.return_value = ClassificationResult(
            tags=[],
            rationale={},
            matched_keywords={}
        )
        
        result = tags_module.run_suggest(
            title="Some random text",
            description="",
            ticket_id=None
        )
        
        assert result == 0
        captured = capsys.readouterr()
        assert "no component tags suggested" in captured.out


class TestRunClassifyText:
    """Tests for run_classify_text function."""

    @patch.object(tags_module, "classify_components")
    def test_classify_text_basic(self, mock_classify: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test basic text classification."""
        mock_classify.return_value = ClassificationResult(
            tags=["component:config"],
            rationale={"component:config": "Config keywords"},
            matched_keywords={"component:config": ["config", "settings"]}
        )
        
        result = tags_module.run_classify_text("Update config file")
        
        assert result == 0
        captured = capsys.readouterr()
        assert "component:config" in captured.out

    @patch.object(tags_module, "classify_components")
    def test_classify_text_json_output(self, mock_classify: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test JSON output for text classification."""
        mock_classify.return_value = ClassificationResult(
            tags=["component:tests"],
            rationale={},
            matched_keywords={}
        )
        
        result = tags_module.run_classify_text("Add tests", json_output=True)
        
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "tags" in output


class TestRunShowKeywords:
    """Tests for run_show_keywords function."""

    @patch.object(tags_module, "get_keyword_map_documentation", return_value="Keyword docs")
    def test_show_keywords(self, mock_docs: MagicMock, capsys: pytest.CaptureFixture) -> None:
        """Test showing keyword documentation."""
        result = tags_module.run_show_keywords()
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Keyword docs" in captured.out


class TestBuildSuggestParser:
    """Tests for build_suggest_parser."""

    def test_suggest_parser_has_ticket_option(self) -> None:
        """Test --ticket option exists."""
        parser = tags_module.build_suggest_parser()
        args = parser.parse_args(["--ticket", "abc-123"])
        assert args.ticket == "abc-123"

    def test_suggest_parser_has_description_option(self) -> None:
        """Test --description option exists."""
        parser = tags_module.build_suggest_parser()
        args = parser.parse_args(["--description", "Some desc"])
        assert args.description == "Some desc"

    def test_suggest_parser_has_json_flag(self) -> None:
        """Test --json flag exists."""
        parser = tags_module.build_suggest_parser()
        args = parser.parse_args(["--json"])
        assert args.json is True

    def test_suggest_parser_has_rationale_flag(self) -> None:
        """Test --rationale flag exists."""
        parser = tags_module.build_suggest_parser()
        args = parser.parse_args(["--rationale"])
        assert args.rationale is True

    def test_suggest_parser_accepts_title(self) -> None:
        """Test positional title argument."""
        parser = tags_module.build_suggest_parser()
        args = parser.parse_args(["Ticket title"])
        assert args.title == "Ticket title"


class TestBuildClassifyParser:
    """Tests for build_classify_parser."""

    def test_classify_parser_requires_text(self) -> None:
        """Test that text is required."""
        parser = tags_module.build_classify_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_classify_parser_accepts_text(self) -> None:
        """Test positional text argument."""
        parser = tags_module.build_classify_parser()
        args = parser.parse_args(["some text to classify"])
        assert args.text == "some text to classify"


class TestSuggestMain:
    """Tests for suggest_main entry point."""

    @patch.object(tags_module, "run_suggest", return_value=0)
    def test_suggest_main_calls_run_suggest(self, mock_run: MagicMock) -> None:
        """Test that suggest_main calls run_suggest."""
        result = tags_module.suggest_main(["Ticket title"])
        assert result == 0
        mock_run.assert_called_once()


class TestClassifyMain:
    """Tests for classify_main entry point."""

    @patch.object(tags_module, "run_classify_text", return_value=0)
    def test_classify_main_calls_run_classify(self, mock_run: MagicMock) -> None:
        """Test that classify_main calls run_classify_text."""
        result = tags_module.classify_main(["some text"])
        assert result == 0
        mock_run.assert_called_once()


class TestKeywordsMain:
    """Tests for keywords_main entry point."""

    @patch.object(tags_module, "run_show_keywords", return_value=0)
    def test_keywords_main_calls_run_show(self, mock_run: MagicMock) -> None:
        """Test that keywords_main calls run_show_keywords."""
        result = tags_module.keywords_main([])
        assert result == 0
        mock_run.assert_called_once()
