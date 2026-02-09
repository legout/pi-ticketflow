"""CLI entry point for demo package.

Examples:
    $ python -m demo
    Hello, World!
    $ python -m demo Alice
    Hello, Alice!
    $ python -m demo "Alice Smith"
    Hello, Alice Smith!
    $ python -m demo ""
    Hello, World!
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional
from collections.abc import Sequence

from demo.hello import hello


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the hello CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        int: Exit code (0 for success).
    """
    parser = argparse.ArgumentParser(
        prog="demo",
        description="Print a hello message",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="World",
        help="Name to greet (default: World)",
    )

    args: argparse.Namespace = parser.parse_args(argv)
    print(hello(args.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
