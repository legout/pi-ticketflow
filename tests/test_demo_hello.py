"""Tests for demo hello module.

Test suite for the hello-world utility demonstrating IRF workflow.
Covers default parameter, custom names, and edge cases.
"""

from __future__ import annotations

import pytest

from demo.hello import hello
from demo.__main__ import main

pytestmark = pytest.mark.unit


def test_hello_default() -> None:
    """Test hello with default name."""
    result = hello()
    assert result == "Hello, World!"


def test_hello_custom_name() -> None:
    """Test hello with custom name."""
    result = hello("Alice")
    assert result == "Hello, Alice!"


def test_hello_empty_string() -> None:
    """Test hello with empty string falls back to World."""
    result = hello("")
    assert result == "Hello, World!"


def test_hello_whitespace_only() -> None:
    """Test hello with whitespace-only strings fall back to World."""
    # Various whitespace characters (spaces, tabs, newlines)
    for whitespace in ["   ", "\t\n\r", "  \t\n  "]:
        result = hello(whitespace)
        assert result == "Hello, World!", f"Failed for whitespace: {repr(whitespace)}"


def test_hello_whitespace_stripped() -> None:
    """Test hello strips leading/trailing whitespace from names."""
    result = hello("  Alice  ")
    assert result == "Hello, Alice!"
    result = hello("\tBob\n")
    assert result == "Hello, Bob!"


def test_hello_internal_whitespace_normalized() -> None:
    """Test hello collapses internal whitespace runs to a single space."""
    result = hello("Alice   Bob")
    assert result == "Hello, Alice Bob!"
    result = hello("Alice\t\t\nBob")
    assert result == "Hello, Alice Bob!"


def test_hello_unicode_whitespace_stripped() -> None:
    """Test hello strips Unicode zero-width whitespace characters."""
    # Zero-width space (U+200B), zero-width non-joiner (U+200C), zero-width joiner (U+200D)
    # and zero-width no-break space (U+FEFF) should be stripped
    for zw_char in ["\u200B", "\u200C", "\u200D", "\uFEFF"]:
        result = hello(f"{zw_char}Alice{zw_char}")
        assert result == "Hello, Alice!", f"Failed for zero-width char: U+{ord(zw_char):04X}"
    # Multiple zero-width chars and mixed with regular whitespace
    result = hello("\u200B\u200C \tAlice\n\uFEFF")
    assert result == "Hello, Alice!"
    # Zero-width only should fall back to World
    result = hello("\u200B\u200C\u200D")
    assert result == "Hello, World!"


def test_hello_zero_width_inside_word() -> None:
    """Test zero-width characters inside words are removed without adding spaces."""
    # Zero-width chars embedded inside a word should NOT create spaces
    result = hello("Ali\u200Bce")  # U+200B zero-width space
    assert result == "Hello, Alice!", f"Expected 'Hello, Alice!' but got {result!r}"
    result = hello("Jo\u200Chn")  # U+200C zero-width non-joiner
    assert result == "Hello, John!", f"Expected 'Hello, John!' but got {result!r}"
    result = hello("Te\u200Dst")  # U+200D zero-width joiner
    assert result == "Hello, Test!", f"Expected 'Hello, Test!' but got {result!r}"
    result = hello("Bo\uFEFFb")  # U+FEFF zero-width no-break space
    assert result == "Hello, Bob!", f"Expected 'Hello, Bob!' but got {result!r}"


def test_cli_default(capsys: pytest.CaptureFixture[str]) -> None:
    """Test CLI entry point with no arguments."""
    result = main([])
    assert result == 0
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out


def test_cli_with_name(capsys: pytest.CaptureFixture[str]) -> None:
    """Test CLI entry point with a name argument."""
    result = main(["Alice"])
    assert result == 0
    captured = capsys.readouterr()
    assert "Hello, Alice!" in captured.out


def test_cli_empty_string(capsys: pytest.CaptureFixture[str]) -> None:
    """Test CLI entry point with empty string argument."""
    result = main([""])
    assert result == 0
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out


def test_hello_none_raises() -> None:
    """Test hello with None raises TypeError."""
    with pytest.raises(TypeError, match="name must be a string, got None"):
        hello(None)  # type: ignore[arg-type]


def test_hello_non_string_raises() -> None:
    """Test hello with non-string types raises TypeError."""
    with pytest.raises(TypeError, match="name must be a string, got int"):
        hello(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="name must be a string, got list"):
        hello(["Alice"])  # type: ignore[arg-type]


def test_module_exports() -> None:
    """Test that __all__ exports are correct."""
    from demo import __all__ as demo_all
    from demo.hello import __all__ as hello_all

    assert demo_all == ["hello"]
    assert hello_all == ["hello"]
