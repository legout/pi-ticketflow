"""Hello-world utility for demo purposes.

This module provides a simple greeting function for demonstrating
the IRF (Implement-Review-Fix) workflow. Ticket: abc-123

The module exposes a single function `hello()` that returns a greeting
string. It can be used as a library import or run as a CLI script.

Examples:
    >>> from demo.hello import hello
    >>> hello()
    'Hello, World!'
    >>> hello("Alice")
    'Hello, Alice!'

CLI Usage:
    $ python -m demo
    Hello, World!
    $ python -m demo Alice
    Hello, Alice!
"""

from __future__ import annotations

import re

# Pre-compiled regex for performance
# Matches zero-width chars (U+200B-U+200D, U+FEFF) and whitespace
_ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\uFEFF]+")
_WHITESPACE_RE = re.compile(r"\s+")


def hello(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".
            Zero-width Unicode characters (U+200B-U+200D, U+FEFF) are removed.
            Then all whitespace runs (including internal) are collapsed to a
            single space, and leading/trailing whitespace is stripped.
            If the result is empty after cleaning, "Hello, World!" is returned.

    Returns:
        str: A greeting string in the format "Hello, {name}!".

    Raises:
        TypeError: If name is not a string type. Note: This is only raised
            when calling the function directly. The CLI interface will treat
            non-string input as a string argument and not raise TypeError.
    """
    if not isinstance(name, str):
        # Special-case None for better error message
        type_name = "None" if name is None else type(name).__name__
        raise TypeError(f"name must be a string, got {type_name}")
    # Step 1: Remove zero-width chars first (U+200B-U+200D, U+FEFF)
    name_no_zw = _ZERO_WIDTH_RE.sub("", name)
    # Step 2: Collapse whitespace runs to single space
    cleaned_name = _WHITESPACE_RE.sub(" ", name_no_zw).strip()
    if not cleaned_name:
        return "Hello, World!"
    return f"Hello, {cleaned_name}!"


__all__ = ["hello"]
