"""Version information for tf_cli."""
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_version() -> str:
    """Read version from VERSION file with fallback."""
    try:
        with open(os.path.join(_ROOT, "VERSION")) as f:
            return f.read().strip()
    except (FileNotFoundError, IOError):
        return "unknown"


__version__ = _read_version()
