from __future__ import annotations

"""Hello-world utility for demo purposes.

This module provides a simple greeting function for demonstrating
the IRF (Implement-Review-Fix) workflow. Ticket: abc-123
"""

import sys


def hello(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        str: A greeting string in the format "Hello, {name}!".
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "World"
    print(hello(name))
