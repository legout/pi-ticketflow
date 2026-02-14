"""Ralph subpackage for queue state and scheduler utilities."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_ralph_module() -> ModuleType:
    """Load the main ralph.py module from the parent directory.
    
    This is needed because there's both a tf/ralph.py module and tf/ralph/ package,
    and we need to expose items from both.
    """
    # Find the main ralph.py module
    ralph_py_path = Path(__file__).parent.parent / "ralph.py"
    spec = importlib.util.spec_from_file_location("_ralph_main", ralph_py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load ralph module from {ralph_py_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["_ralph_main"] = module
    spec.loader.exec_module(module)
    return module


# Load the main ralph module
_ralph_module = _load_ralph_module()

# Re-export main Ralph module items for backward compatibility
# Core classes and functions
DEFAULTS: dict[str, Any] = _ralph_module.DEFAULTS
ProgressDisplay = _ralph_module.ProgressDisplay
_validate_pi_output = _ralph_module._validate_pi_output
parse_run_args = _ralph_module.parse_run_args
parse_start_args = _ralph_module.parse_start_args
run_ticket = _ralph_module.run_ticket

# Expose functions that tests may need to patch
usage = _ralph_module.usage
utc_now = _ralph_module.utc_now
ensure_ralph_dir = _ralph_module.ensure_ralph_dir
load_config = _ralph_module.load_config
json_load = _ralph_module.json_load
run_shell = _ralph_module.run_shell
sanitize_ticket_query = _ralph_module.sanitize_ticket_query
ticket_list_query = _ralph_module.ticket_list_query
select_ticket = _ralph_module.select_ticket
list_ready_tickets = _ralph_module.list_ready_tickets
list_blocked_tickets = _ralph_module.list_blocked_tickets
backlog_empty = _ralph_module.backlog_empty
ensure_pi = _ralph_module.ensure_pi
prompt_exists = _ralph_module.prompt_exists
build_cmd = _ralph_module.build_cmd
_run_with_timeout = _ralph_module._run_with_timeout
extract_components = _ralph_module.extract_components
select_parallel_tickets = _ralph_module.select_parallel_tickets
git_repo_root = _ralph_module.git_repo_root
parse_bool = _ralph_module.parse_bool
resolve_log_level = _ralph_module.resolve_log_level
log_level_to_flag = _ralph_module.log_level_to_flag
resolve_attempt_timeout_ms = _ralph_module.resolve_attempt_timeout_ms
resolve_max_restarts = _ralph_module.resolve_max_restarts
resolve_timeout_backoff_enabled = _ralph_module.resolve_timeout_backoff_enabled
resolve_timeout_backoff_increment_ms = _ralph_module.resolve_timeout_backoff_increment_ms
resolve_timeout_backoff_max_ms = _ralph_module.resolve_timeout_backoff_max_ms
calculate_effective_timeout = _ralph_module.calculate_effective_timeout
resolve_session_dir = _ralph_module.resolve_session_dir
resolve_knowledge_dir = _ralph_module.resolve_knowledge_dir
lock_acquire = _ralph_module.lock_acquire
lock_release = _ralph_module.lock_release
ensure_progress = _ralph_module.ensure_progress
set_state = _ralph_module.set_state
clear_ticket_title_cache = _ralph_module.clear_ticket_title_cache
extract_ticket_title = _ralph_module.extract_ticket_title
extract_ticket_titles = _ralph_module.extract_ticket_titles
extract_summary_and_commit = _ralph_module.extract_summary_and_commit
extract_issue_counts = _ralph_module.extract_issue_counts
extract_lesson_block = _ralph_module.extract_lesson_block
update_state = _ralph_module.update_state

# Retry state management functions
load_retry_state = _ralph_module.load_retry_state
is_ticket_blocked_by_retries = _ralph_module.is_ticket_blocked_by_retries
resolve_max_retries_from_settings = _ralph_module.resolve_max_retries_from_settings
resolve_escalation_enabled = _ralph_module.resolve_escalation_enabled

# Dispatch functions from ralph.py
DispatchResult = _ralph_module.DispatchResult
run_ticket_dispatch = _ralph_module.run_ticket_dispatch

# Expose main entry point functions
ralph_start = _ralph_module.ralph_start
ralph_run = _ralph_module.ralph_run
main = _ralph_module.main

# Expose modules that tests may need to patch
subprocess = _ralph_module.subprocess
sys_mod = _ralph_module.sys
os_mod = _ralph_module.os

# Import from queue_state module
from tf.ralph.queue_state import QueueStateSnapshot, get_queue_state

# Import completion handling functions from completion module
from tf.ralph_completion import (
    DispatchCompletionResult,
    DispatchCompletionStatus,
    cleanup_dispatch_tracking,
    graceful_terminate_dispatch,
    poll_dispatch_status,
    update_dispatch_tracking_status,
    wait_for_dispatch_completion,
)

# Import from utils for backward compatibility with tests that patch these
from tf.utils import find_project_root

__all__ = [
    "QueueStateSnapshot",
    "get_queue_state",
    "DEFAULTS",
    "ProgressDisplay",
    "_validate_pi_output",
    "parse_run_args",
    "parse_start_args",
    "run_ticket",
    "ralph_start",
    "ralph_run",
    "main",
    # Completion handling
    "DispatchResult",
    "run_ticket_dispatch",
    "DispatchCompletionResult",
    "DispatchCompletionStatus",
    "poll_dispatch_status",
    "graceful_terminate_dispatch",
    "wait_for_dispatch_completion",
    "cleanup_dispatch_tracking",
    "update_dispatch_tracking_status",
]
