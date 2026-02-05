import sys
from typing import Optional, List

from . import init_new, login_new, ralph_new, sync_new, update_new


def usage() -> None:
    print(
        """Ticketflow (new Python CLI)

Usage:
  tf new init [--project <path>]
  tf new login [--project <path>] [--global]
  tf new ralph <subcommand> [options]
  tf new sync [--project <path>] [--global]
  tf new update [--project <path>] [--global]

Commands:
  init    Create .tf project scaffolding
  login   Configure API keys for web search and MCP servers
  ralph   Python implementation of Ralph loop (start/run)
  sync    Sync model frontmatter from config
  update  Download latest agents/skills/prompts
"""
    )


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in {"-h", "--help", "help"}:
        usage()
        return 0

    command = argv[0]
    rest = argv[1:]

    if command == "init":
        return init_new.main(rest)
    if command == "login":
        return login_new.main(rest)
    if command == "ralph":
        return ralph_new.main(rest)
    if command == "sync":
        return sync_new.main(rest)
    if command == "update":
        return update_new.main(rest)

    print(f"Unknown 'new' subcommand: {command}", file=sys.stderr)
    usage()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
