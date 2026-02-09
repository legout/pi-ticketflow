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


def hello(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        str: A greeting string in the format "Hello, {name}!".
    """
    if not name.strip():
        name = "World"
    return f"Hello, {name}!"
