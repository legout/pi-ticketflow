"""Session recovery helpers exposed at tf.session_recovery.

This module intentionally avoids importing ``tf.ralph.session_recovery`` directly,
because ``tf/ralph.py`` is a module (not a package) and can shadow the
``tf/ralph/`` package name during import.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_impl() -> ModuleType:
    impl_path = Path(__file__).with_name("ralph") / "session_recovery.py"
    spec = importlib.util.spec_from_file_location("_tf_session_recovery_impl", impl_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load session recovery module from {impl_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_tf_session_recovery_impl"] = module
    spec.loader.exec_module(module)
    return module


_impl = _load_impl()

DEFAULT_SESSION_TTL_MS = _impl.DEFAULT_SESSION_TTL_MS
DispatchSessionState = _impl.DispatchSessionState
get_process_start_time = _impl.get_process_start_time
register_dispatch_session = _impl.register_dispatch_session
run_startup_recovery = _impl.run_startup_recovery
update_dispatch_session_status = _impl.update_dispatch_session_status

__all__ = [
    "DEFAULT_SESSION_TTL_MS",
    "DispatchSessionState",
    "get_process_start_time",
    "register_dispatch_session",
    "run_startup_recovery",
    "update_dispatch_session_status",
]
