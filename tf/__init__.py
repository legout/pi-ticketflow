"""Ticketflow CLI - IRF workflow toolkit for Pi.

This is the canonical tf package. The tf_cli package is maintained for backward compatibility
through version 0.4.x and will be removed in 0.5.0.

Migration progress (pt-tupn):
- CLI dispatch code now lives under tf/
- Core modules: new_cli, setup, login moved to tf/
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

try:
    from importlib.metadata import version as dist_version, PackageNotFoundError
except Exception:  # pragma: no cover - ultra-defensive fallback
    dist_version = None
    PackageNotFoundError = Exception


def _resolve_repo_root() -> Optional[Path]:
    """Find the repository root by looking for markers."""
    module_dir = Path(__file__).resolve().parent
    for parent in [module_dir, *module_dir.parents]:
        if (parent / ".tf").is_dir() and (parent / "VERSION").is_file():
            return parent
        if (parent / "pyproject.toml").is_file() and (parent / "tf").is_dir():
            return parent
    return None


def _read_version_file(path: Path) -> Optional[str]:
    """Safely read version from a file."""
    try:
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    except OSError:
        pass
    return None


def _get_git_tag_version(repo_root: Optional[Path] = None) -> Optional[str]:
    """Get version from git tag."""
    try:
        git_cwd = str(repo_root) if repo_root else "."
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True,
            cwd=git_cwd,
            check=False,
        )
        if result.returncode == 0:
            tag = result.stdout.strip()
            return tag[1:] if tag.startswith("v") else tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=git_cwd,
            check=False,
        )
        if result.returncode == 0:
            tag = result.stdout.strip()
            return tag[1:] if tag.startswith("v") else tag
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return None


def _get_installed_package_version() -> Optional[str]:
    """Get version from installed package metadata (wheel/sdist/uvx installs)."""
    if dist_version is None:
        return None

    for name in ("pi-tk-workflow", "pi_ticketflow", "tf"):
        try:
            value = dist_version(name)
            if value:
                return value
        except PackageNotFoundError:
            continue
        except Exception:
            continue
    return None


def _read_version() -> str:
    """Read version from VERSION file, git tag, or return 'unknown'."""
    # Try repo root first (for git checkouts/development)
    repo_root = _resolve_repo_root()
    if repo_root:
        version = _read_version_file(repo_root / "VERSION")
        if version:
            return version

    # Try relative to this module (for pip/uvx installs)
    package_root = Path(__file__).resolve().parent.parent
    version = _read_version_file(package_root / "VERSION")
    if version:
        return version

    # Try git tag as third fallback (for git checkouts without VERSION file)
    if repo_root:
        git_version = _get_git_tag_version(repo_root)
        if git_version:
            return git_version

    # Final fallback for packaged installs (pip/uvx/wheels)
    installed = _get_installed_package_version()
    if installed:
        return installed

    return "unknown"


__version__ = _read_version()


def get_version() -> str:
    """Return the current version string."""
    return _read_version()


# Re-export ticket_factory for convenient access
from tf.ticket_factory import TicketDef, CreatedTicket, create_tickets, score_tickets

__all__ = [
    "__version__",
    "get_version",
    "TicketDef",
    "CreatedTicket",
    "create_tickets",
    "score_tickets",
]
