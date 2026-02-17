"""Self-update command for the global tf CLI.

Updates the tf CLI to the latest version using uvx.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

DEFAULT_UVX_SOURCE = "git+https://github.com/legout/pi-ticketflow"


def get_installed_version() -> Optional[str]:
    """Get currently installed tf version."""
    try:
        import tf
        return tf.get_version()
    except Exception:
        return None


def get_latest_version(uvx_source: str) -> Optional[str]:
    """Check the latest version available from the source."""
    try:
        # Try to get version from git repo without full clone
        result = subprocess.run(
            ["git", "ls-remote", "--tags", uvx_source.replace("git+", ""), "*"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            # Parse tags and find latest version
            tags = []
            for line in result.stdout.strip().split("\n"):
                if "refs/tags/" in line:
                    tag = line.split("refs/tags/")[-1].strip()
                    if tag.startswith("v"):
                        tags.append(tag)
            if tags:
                # Sort by version number
                return sorted(tags, key=lambda x: x.lstrip("v").split("."))[-1]
    except Exception:
        pass

    # Fallback: try pip index
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", "pi-tk-workflow"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and "Available versions:" in result.stdout:
            # Parse versions from output
            import re
            match = re.search(r"Available versions:\s*([\d.,\s]+)", result.stdout)
            if match:
                versions = [v.strip() for v in match.group(1).split(",")]
                return f"v{versions[0]}" if versions else None
    except Exception:
        pass

    return None


def update_via_uvx(uvx_source: str, force: bool = False) -> bool:
    """Update tf using uvx."""
    uvx = shutil.which("uvx")
    if not uvx:
        print("ERROR: uvx not found in PATH. Cannot self-update.", file=sys.stderr)
        print("Install uvx: https://github.com/astral-sh/uv", file=sys.stderr)
        return False

    print(f"Updating tf from: {uvx_source}")

    # Clear uvx cache for this package to force fresh install
    if force:
        print("Clearing uvx cache...")
        try:
            subprocess.run(
                [uvx, "cache", "clean", "pi-tk-workflow"],
                capture_output=True,
                timeout=30,
            )
        except Exception:
            pass  # Cache clear is best-effort

    # Re-install via uvx to update
    cmd = [uvx, "--from", uvx_source, "tf", "--version"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            new_version = result.stdout.strip()
            print(f"✓ Successfully updated to: {new_version}")
            return True
        else:
            print(f"ERROR: Update failed: {result.stderr}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("ERROR: Update timed out. Check your network connection.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Update failed: {e}", file=sys.stderr)
        return False


def update_cli_shim(uvx_source: str) -> bool:
    """Update the CLI shim if installed."""
    shim_path = Path.home() / ".local/bin/tf"
    if not shim_path.exists():
        return True  # No shim to update

    # Update the source reference in the shim
    cli_source_file = Path.home() / ".tf/cli-source"
    if cli_source_file.exists():
        try:
            cli_source_file.write_text(uvx_source + "\n", encoding="utf-8")
            print(f"✓ Updated CLI source reference: {cli_source_file}")
        except Exception as e:
            print(f"WARNING: Could not update source reference: {e}", file=sys.stderr)

    return True


def prompt_yes_no(message: str, default_yes: bool) -> bool:
    """Prompt user for yes/no input."""
    suffix = "(Y/n)" if default_yes else "(y/N)"
    reply = input(f"{message} {suffix} ").strip().lower()
    if not reply:
        return default_yes
    return reply.startswith("y")


def run_self_update(args: argparse.Namespace) -> int:
    """Run the self-update command."""
    uvx_source = args.source or os.environ.get("TF_UVX_FROM") or DEFAULT_UVX_SOURCE

    current_version = get_installed_version()
    print(f"Current version: {current_version or 'unknown'}")

    if not args.yes:
        if not prompt_yes_no("Update tf to the latest version?", default_yes=True):
            print("Update cancelled.")
            return 0

    print("\nUpdating tf CLI...")

    # Update the CLI via uvx
    if not update_via_uvx(uvx_source, force=args.force):
        return 1

    # Update shim if present
    if not update_cli_shim(uvx_source):
        return 1

    # Verify installation
    new_version = get_installed_version()
    if new_version:
        print(f"\n✓ tf is now at version: {new_version}")
    else:
        print("\n✓ Update complete (version check unavailable)")

    print("\nNote: Project workflow assets are updated separately via 'tf update'")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for self-update command."""
    parser = argparse.ArgumentParser(
        description="Update the tf CLI to the latest version"
    )
    parser.add_argument(
        "--source",
        help="Source to update from (default: git+https://github.com/legout/pi-ticketflow)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update (clear cache)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for self-update command."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_self_update(args)


if __name__ == "__main__":
    raise SystemExit(main())
