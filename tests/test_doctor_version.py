"""Tests for tf doctor version check functionality.

This module contains comprehensive tests for the version check functionality
in tf_cli/doctor_new.py, covering all version-related functions with
normal paths, edge cases, and error conditions.

Uses pytest fixtures (tmp_path, capsys) for isolated test environments
and unittest.mock for testing error conditions.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from tf_cli.doctor_new import (
    check_version_consistency,
    get_package_version,
    get_version_file_version,
    normalize_version,
    sync_version_file,
)


class TestGetPackageVersion:
    """Tests for get_package_version function."""

    def test_returns_version_from_package_json(self, tmp_path: Path) -> None:
        """Should return version string from valid package.json."""

        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        
        result = get_package_version(tmp_path)
        
        assert result == "1.2.3"

    def test_returns_none_when_package_json_missing(self, tmp_path: Path) -> None:
        """Should return None when package.json doesn't exist."""
        result = get_package_version(tmp_path)
        
        assert result is None

    def test_returns_none_when_version_missing(self, tmp_path: Path) -> None:
        """Should return None when version field is missing."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"name": "test-package"}))
        
        result = get_package_version(tmp_path)
        
        assert result is None

    def test_returns_none_when_version_is_empty_string(self, tmp_path: Path) -> None:
        """Should return None when version is empty string."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": ""}))
        
        result = get_package_version(tmp_path)
        
        assert result is None

    def test_returns_none_when_version_is_whitespace(self, tmp_path: Path) -> None:
        """Should return None when version is whitespace only."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "   "}))
        
        result = get_package_version(tmp_path)
        
        assert result is None

    def test_returns_none_when_version_is_not_string(self, tmp_path: Path) -> None:
        """Should return None when version is not a string (e.g., number)."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": 123}))
        
        result = get_package_version(tmp_path)
        
        assert result is None

    def test_strips_whitespace_from_version(self, tmp_path: Path) -> None:
        """Should strip whitespace from version string."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "  1.2.3  "}))
        
        result = get_package_version(tmp_path)
        
        assert result == "1.2.3"

    def test_returns_none_on_invalid_json(self, tmp_path: Path) -> None:
        """Should return None when package.json contains invalid JSON."""
        package_file = tmp_path / "package.json"
        package_file.write_text("not valid json")
        
        result = get_package_version(tmp_path)
        
        assert result is None


class TestGetVersionFileVersion:
    """Tests for get_version_file_version function."""

    def test_returns_version_from_version_file(self, tmp_path: Path) -> None:
        """Should return version string from VERSION file."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")
        
        result = get_version_file_version(tmp_path)
        
        assert result == "1.2.3"

    def test_returns_none_when_version_file_missing(self, tmp_path: Path) -> None:
        """Should return None when VERSION file doesn't exist."""
        result = get_version_file_version(tmp_path)
        
        assert result is None

    def test_returns_none_when_version_file_empty(self, tmp_path: Path) -> None:
        """Should return None when VERSION file is empty."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("")
        
        result = get_version_file_version(tmp_path)
        
        assert result is None

    def test_strips_whitespace_and_newlines(self, tmp_path: Path) -> None:
        """Should strip whitespace and newlines from version."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("  1.2.3\n\n  ")
        
        result = get_version_file_version(tmp_path)
        
        assert result == "1.2.3"

    def test_returns_none_on_read_error(self, tmp_path: Path) -> None:
        """Should return None when VERSION file cannot be read."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")
        
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("Permission denied")):
            result = get_version_file_version(tmp_path)
        
        assert result is None


class TestNormalizeVersion:
    """Tests for normalize_version function."""

    @pytest.mark.parametrize(
        "input_version,expected",
        [
            ("1.2.3", "1.2.3"),
            ("2.0.0-beta", "2.0.0-beta"),
            ("v1.2.3", "1.2.3"),
            ("v2.0.0", "2.0.0"),
            ("V1.2.3", "1.2.3"),
            ("V2.0.0", "2.0.0"),
            ("", ""),
            ("v1.0.0-alpha", "1.0.0-alpha"),
            ("v1.0.0v2", "1.0.0v2"),
        ],
    )
    def test_normalize_version(self, input_version: str, expected: str) -> None:
        """Should correctly normalize version strings."""

        result = normalize_version(input_version)
        assert result == expected


class TestSyncVersionFile:
    """Tests for sync_version_file function."""

    def test_creates_version_file_when_missing(self, tmp_path: Path) -> None:
        """Should create VERSION file when it doesn't exist."""
        version_file = tmp_path / "VERSION"
        
        result = sync_version_file(tmp_path, "1.2.3")
        
        assert result is True
        assert version_file.exists()
        assert version_file.read_text().strip() == "1.2.3"

    def test_updates_existing_version_file(self, tmp_path: Path) -> None:
        """Should update VERSION file when it exists with different version."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("0.9.0")
        
        result = sync_version_file(tmp_path, "1.2.3")
        
        assert result is True
        assert version_file.read_text().strip() == "1.2.3"

    def test_avoids_unnecessary_write_when_content_unchanged(self, tmp_path: Path) -> None:
        """Should skip write when file already has correct content with newline."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3\n")
        original_stat = version_file.stat()
        
        result = sync_version_file(tmp_path, "1.2.3")
        
        assert result is True
        new_stat = version_file.stat()
        # Verify file was not rewritten (mtime unchanged)
        assert new_stat.st_mtime == original_stat.st_mtime

    def test_writes_when_content_differs(self, tmp_path: Path) -> None:
        """Should update file when version differs (no trailing newline case)."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")  # No newline
        
        result = sync_version_file(tmp_path, "1.2.3")
        
        assert result is True
        assert version_file.read_text() == "1.2.3\n"

    def test_adds_newline_to_version(self, tmp_path: Path) -> None:
        """Should add trailing newline to version in file."""
        version_file = tmp_path / "VERSION"
        
        sync_version_file(tmp_path, "1.2.3")
        
        assert version_file.read_text() == "1.2.3\n"

    def test_returns_false_on_write_error(self, tmp_path: Path) -> None:
        """Should return False when VERSION file cannot be written."""
        with mock.patch.object(Path, "write_text", side_effect=PermissionError("Permission denied")):
            result = sync_version_file(tmp_path, "1.2.3")
        
        assert result is False


class TestCheckVersionConsistency:
    """Tests for check_version_consistency function."""

    def test_returns_true_when_no_package_json(self, tmp_path: Path, capsys) -> None:
        """Should return True when no package.json exists."""
        result = check_version_consistency(tmp_path)
        
        assert result is True
        captured = capsys.readouterr()
        assert "No package.json found" in captured.out

    def test_returns_true_when_package_json_has_no_version(self, tmp_path: Path, capsys) -> None:
        """Should return True when package.json has no version field."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"name": "test"}))
        
        result = check_version_consistency(tmp_path)
        
        assert result is True
        captured = capsys.readouterr()
        assert "version field is missing or invalid" in captured.out

    def test_returns_true_when_only_package_json_exists(self, tmp_path: Path, capsys) -> None:
        """Should return True when only package.json exists with valid version."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        
        result = check_version_consistency(tmp_path)
        
        assert result is True
        captured = capsys.readouterr()
        assert "[ok] package.json version: 1.2.3" in captured.out
        assert "No VERSION file found" in captured.out

    def test_returns_true_when_versions_match(self, tmp_path: Path, capsys) -> None:
        """Should return True when VERSION file matches package.json."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")
        
        result = check_version_consistency(tmp_path)
        
        assert result is True
        captured = capsys.readouterr()
        assert "VERSION file matches package.json" in captured.out

    def test_returns_true_with_v_prefix_normalization(self, tmp_path: Path, capsys) -> None:
        """Should return True when versions match after v prefix normalization."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        version_file = tmp_path / "VERSION"
        version_file.write_text("v1.2.3")
        
        result = check_version_consistency(tmp_path)
        
        assert result is True
        captured = capsys.readouterr()
        assert "VERSION file matches package.json" in captured.out

    def test_returns_false_when_versions_mismatch(self, tmp_path: Path, capsys) -> None:
        """Should return False when VERSION file doesn't match package.json."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        version_file = tmp_path / "VERSION"
        version_file.write_text("0.9.0")
        
        result = check_version_consistency(tmp_path)
        
        assert result is False
        captured = capsys.readouterr()
        assert "does not match package.json" in captured.out

    def test_fix_creates_version_file_when_missing(self, tmp_path: Path, capsys) -> None:
        """Should create VERSION file when fix=True and file is missing."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        
        result = check_version_consistency(tmp_path, fix=True)
        
        assert result is True
        version_file = tmp_path / "VERSION"
        assert version_file.exists()
        assert version_file.read_text().strip() == "1.2.3"
        captured = capsys.readouterr()
        assert "VERSION file created" in captured.out

    def test_fix_updates_mismatched_version(self, tmp_path: Path, capsys) -> None:
        """Should update VERSION file when fix=True and versions mismatch."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        version_file = tmp_path / "VERSION"
        version_file.write_text("0.9.0")
        
        result = check_version_consistency(tmp_path, fix=True)
        
        assert result is True
        assert version_file.read_text().strip() == "1.2.3"
        captured = capsys.readouterr()
        assert "VERSION file updated" in captured.out

    def test_dry_run_shows_would_create(self, tmp_path: Path, capsys) -> None:
        """Should show what would be created without creating in dry-run mode."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        
        result = check_version_consistency(tmp_path, dry_run=True)
        
        assert result is False
        version_file = tmp_path / "VERSION"
        assert not version_file.exists()
        captured = capsys.readouterr()
        assert "Would create VERSION file" in captured.out

    def test_dry_run_shows_would_update(self, tmp_path: Path, capsys) -> None:
        """Should show what would be updated without updating in dry-run mode."""
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"version": "1.2.3"}))
        version_file = tmp_path / "VERSION"
        version_file.write_text("0.9.0")
        
        result = check_version_consistency(tmp_path, dry_run=True)
        
        assert result is False
        assert version_file.read_text().strip() == "0.9.0"  # Unchanged
        captured = capsys.readouterr()
        assert "Would update VERSION file" in captured.out
