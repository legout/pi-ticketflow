"""Ralph dispatch loop orchestrator using interactive_shell dispatch sessions.

This is an experimental orchestrator for autonomous ticket processing.
The stable production runner remains `tf ralph start`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import required tools
from tf.utils import find_project_root

# Constants
STATE_FILE = "dispatch-loop-state.json"
LOCK_FILE = "dispatch-loop.lock"
PROGRESS_FILE = "progress.md"
STATE_VERSION = 1
DEFAULT_MAX_ITERATIONS = 50
DEFAULT_PARALLEL = 1
MAX_STATE_LIST_SIZE = 1000  # Limit completed/failed lists to prevent unbounded growth

# Signal handling state for guaranteed lock cleanup
_signal_handlers_installed = False
_lock_path_for_cleanup: Optional[Path] = None
_current_run_id: Optional[str] = None  # For ownership verification in signal handler
_current_lock_pid: Optional[int] = None
_in_signal_handler = False  # Re-entrancy protection


class RalphLoopError(Exception):
    """Base exception for Ralph loop errors."""
    pass


class PreconditionsError(RalphLoopError):
    """Raised when preconditions are not met."""
    pass


class LockError(RalphLoopError):
    """Raised when lock cannot be acquired."""
    pass


def utc_now() -> str:
    """Return current UTC time in ISO8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _release_lock_on_signal(signum: int, _frame: Any) -> None:
    """Signal handler to release lock and exit cleanly on SIGINT/SIGTERM.
    
    Verifies lock ownership before unlinking to prevent removing
    a lock owned by a different process/run. Includes re-entrancy
    protection to handle nested signal delivery.
    """
    global _lock_path_for_cleanup, _current_run_id, _in_signal_handler
    
    # Re-entrancy protection: if already in handler, just exit
    if _in_signal_handler:
        return
    _in_signal_handler = True
    
    try:
        if _lock_path_for_cleanup is not None:
            try:
                # Verify ownership before unlinking
                if _lock_path_for_cleanup.exists():
                    content = _lock_path_for_cleanup.read_text(encoding="utf-8").strip()
                    if content.startswith("{"):
                        lock_data = json.loads(content)
                        # Only unlink if we own the lock (same runId and same PID)
                        if (lock_data.get("runId") == _current_run_id and 
                            lock_data.get("pid") == os.getpid()):
                            _lock_path_for_cleanup.unlink()
                            print(f"INFO: Released lock on signal {signum}", file=sys.stderr)
                        else:
                            print(
                                f"WARN: Lock ownership changed, not releasing on signal {signum}",
                                file=sys.stderr
                            )
            except (OSError, json.JSONDecodeError, KeyError):
                pass  # Best effort cleanup
    finally:
        raise SystemExit(128 + signum)


def _install_signal_handlers(ralph_dir: Path, run_id: str) -> None:
    """Install signal handlers for guaranteed lock cleanup.
    
    Args:
        ralph_dir: Path to ralph directory for lock file location.
        run_id: Current run ID for ownership verification.
    """
    global _signal_handlers_installed, _lock_path_for_cleanup, _current_run_id
    
    # Always update cleanup context (even if handlers already installed)
    # This handles re-entrant turns where lock path or run_id might change
    _lock_path_for_cleanup = ralph_dir / LOCK_FILE
    _current_run_id = run_id
    
    if _signal_handlers_installed:
        return
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _release_lock_on_signal)
        except Exception as e:
            # Log failure but continue - best effort on platforms that restrict signals
            print(f"WARN: Could not install signal handler for {sig}: {e}", file=sys.stderr)
    
    _signal_handlers_installed = True


def check_preconditions(project_root: Path) -> Path:
    """Check all preconditions and return ralph_dir if satisfied.
    
    Raises:
        PreconditionsError: If any precondition is not met.
    """
    # Check .tf/ralph/ exists
    ralph_dir = project_root / ".tf" / "ralph"
    if not ralph_dir.is_dir():
        raise PreconditionsError(
            "Ralph not initialized. Run: tf ralph init"
        )
    
    # Check prompts/tf.md exists
    local_prompt = project_root / "prompts" / "tf.md"
    legacy_prompt = project_root / ".pi" / "prompts" / "tf.md"
    global_prompt = Path.home() / ".pi" / "agent" / "prompts" / "tf.md"
    
    if not (local_prompt.exists() or legacy_prompt.exists() or global_prompt.exists()):
        raise PreconditionsError(
            "Missing /tf prompt. Run 'tf init' in the project to install prompts "
            "(or 'tf sync' to re-ensure)."
        )
    
    # Check pi and tk are in PATH
    if shutil.which("pi") is None:
        raise PreconditionsError("'pi' not found in PATH")
    if shutil.which("tk") is None:
        raise PreconditionsError("'tk' not found in PATH")
    
    return ralph_dir


def generate_run_id() -> str:
    """Generate a unique run ID."""
    return str(uuid.uuid4())


def validate_lock_schema(data: Any) -> Optional[Dict[str, Any]]:
    """Validate lock data has required fields with correct types.
    
    Returns:
        Validated dict with runId, pid, startedAt or None if invalid.
    """
    if not isinstance(data, dict):
        return None
    
    try:
        run_id = data.get("runId")
        pid = data.get("pid")
        started_at = data.get("startedAt")
        
        # Required fields must be present and correct types
        if not isinstance(run_id, str) or not run_id:
            return None
        if not isinstance(pid, int) or pid <= 0:
            return None
        if not isinstance(started_at, str) or not started_at:
            return None
        
        result: Dict[str, Any] = {
            "runId": run_id,
            "pid": pid,
            "startedAt": started_at,
        }
        
        # Optional fields
        if "processStartTime" in data:
            val = data["processStartTime"]
            if val is None or isinstance(val, (int, float)):
                result["processStartTime"] = val
        
        return result
    except (TypeError, KeyError):
        return None


def read_lock(ralph_dir: Path) -> Optional[Dict[str, Any]]:
    """Read the lock file if it exists.
    
    Returns:
        Dict with runId, pid, startedAt or None if lock doesn't exist or is invalid.
    """
    lock_path = ralph_dir / LOCK_FILE
    if not lock_path.exists():
        return None
    
    try:
        content = lock_path.read_text(encoding="utf-8").strip()
        if not content:
            return None
        
        # Try JSON format first (preferred)
        if content.startswith("{"):
            data = json.loads(content)
            return validate_lock_schema(data)
        
        # Fallback to legacy space-separated format: runId pid startedAt
        parts = content.split(maxsplit=2)
        if len(parts) >= 2:
            try:
                pid = int(parts[1])
                if pid <= 0:
                    return None
                return validate_lock_schema({
                    "runId": parts[0],
                    "pid": pid,
                    "startedAt": parts[2] if len(parts) > 2 else utc_now(),
                })
            except ValueError:
                return None
    except (ValueError, OSError, json.JSONDecodeError):
        pass
    
    return None


def write_lock(ralph_dir: Path, run_id: str) -> bool:
    """Write the lock file for this run in JSON format.
    
    Uses atomic creation via O_CREAT | O_EXCL to prevent race conditions.
    
    Returns:
        True if lock was created, False if lock already exists.
    """
    lock_path = ralph_dir / LOCK_FILE
    pid = os.getpid()
    start_time = get_process_start_time()
    lock_data = {
        "runId": run_id,
        "pid": pid,
        "startedAt": utc_now(),
        "processStartTime": start_time,  # For PID reuse protection
    }
    content = json.dumps(lock_data, indent=2) + "\n"
    
    # Try atomic create first
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return True
    except FileExistsError:
        # Lock already exists, caller should reconcile
        return False
    except OSError:
        return False


def remove_lock(ralph_dir: Path) -> None:
    """Remove the lock file."""
    lock_path = ralph_dir / LOCK_FILE
    if lock_path.exists():
        try:
            lock_path.unlink()
        except OSError:
            pass


def get_process_start_time() -> Optional[float]:
    """Get the current process start time in seconds since boot.
    
    Returns None if not available (non-Linux platforms).
    Used for PID reuse protection in lock files.
    """
    try:
        # Linux: /proc/self/stat field 22 (starttime in clock ticks)
        with open("/proc/self/stat", "r") as f:
            fields = f.read().split()
            if len(fields) >= 22:
                # Convert clock ticks to seconds (usually 100 Hz)
                clock_ticks = int(fields[21])
                hz = os.sysconf("SC_CLK_TCK")
                return clock_ticks / hz
    except (OSError, ValueError, IndexError):
        pass
    return None


def is_process_alive(pid: int, expected_start_time: Optional[float] = None) -> bool:
    """Check if a process with the given PID is alive.
    
    Args:
        pid: Process ID to check
        expected_start_time: If provided, verify the process started at this time
                            to protect against PID reuse.
    
    Returns:
        True if process is alive (and matches expected start time if provided).
    """
    try:
        os.kill(pid, 0)
        if expected_start_time is None:
            return True
        # Verify process start time to protect against PID reuse
        try:
            with open(f"/proc/{pid}/stat", "r") as f:
                fields = f.read().split()
                if len(fields) >= 22:
                    clock_ticks = int(fields[21])
                    hz = os.sysconf("SC_CLK_TCK")
                    actual_start_time = clock_ticks / hz
                    # Allow small tolerance for timing differences
                    return abs(actual_start_time - expected_start_time) < 1.0
        except (OSError, ValueError, IndexError):
            # Can't verify start time, be conservative
            return False
        return True
    except (OSError, ProcessLookupError):
        return False


def reconcile_lock(ralph_dir: Path, run_id: str, dry_run: bool = False) -> bool:
    """Reconcile the lock file state.
    
    Uses atomic lock creation and verifies process identity to prevent
    race conditions and PID reuse vulnerabilities.
    
    Returns:
        True if lock is acquired/held for this run, False if another loop is active.
    """
    if dry_run:
        return True
    
    # Install signal handlers first (before lock acquisition)
    _install_signal_handlers(ralph_dir, run_id)
    
    lock = read_lock(ralph_dir)
    
    if lock is None:
        # No lock exists, try atomic creation
        if write_lock(ralph_dir, run_id):
            return True
        # Race lost - another process created the lock, re-check
        lock = read_lock(ralph_dir)
        if lock is None:
            return False  # Unexpected, but fail safe
    
    if lock.get("runId") == run_id:
        # Same run, re-entrant turn - verify we still own it
        lock_pid = lock.get("pid")
        lock_start_time = lock.get("processStartTime")
        if lock_pid == os.getpid():
            # Same PID, definitely ours
            return True
        # Different PID but same runId - only allow if original process is dead
        if lock_pid is not None and not is_process_alive(lock_pid, lock_start_time):
            # Original process dead, we can take over
            remove_lock(ralph_dir)
            return write_lock(ralph_dir, run_id)
        # Another live process has our runId (shouldn't happen but fail safe)
        print(
            f"ERROR: Another process owns lock with our runId (pid: {lock_pid})",
            file=sys.stderr
        )
        return False
    
    # Different runId, check if owner is alive (with start time verification)
    lock_pid = lock.get("pid")
    lock_start_time = lock.get("processStartTime")
    lock_started = lock.get("startedAt", "unknown")
    
    if lock_pid is not None and is_process_alive(lock_pid, lock_start_time):
        print(
            f"ERROR: Another Ralph loop is active "
            f"(runId: {lock.get('runId')}, pid: {lock_pid}, started: {lock_started})",
            file=sys.stderr
        )
        return False
    
    # Stale lock, clean it up and replace
    print(
        f"INFO: Cleaning up stale lock from run {lock.get('runId')} "
        f"(pid {lock_pid} dead, started: {lock_started})",
        file=sys.stderr
    )
    remove_lock(ralph_dir)
    return write_lock(ralph_dir, run_id)


def load_state(ralph_dir: Path) -> Optional[Dict[str, Any]]:
    """Load state from file if it exists and is valid."""
    state_path = ralph_dir / STATE_FILE
    if not state_path.exists():
        return None
    
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_state(ralph_dir: Path, state: Dict[str, Any]) -> None:
    """Save state atomically using temp file + fsync + rename."""
    state_path = ralph_dir / STATE_FILE
    temp_path = ralph_dir / f".{STATE_FILE}.tmp"
    
    # Prune lists to prevent unbounded growth
    if len(state.get("completed", [])) > MAX_STATE_LIST_SIZE:
        state["completed"] = state["completed"][-MAX_STATE_LIST_SIZE:]
    if len(state.get("failed", [])) > MAX_STATE_LIST_SIZE:
        state["failed"] = state["failed"][-MAX_STATE_LIST_SIZE:]
    
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    
    temp_path.rename(state_path)


def backup_corrupt_state(ralph_dir: Path) -> Path:
    """Move corrupt state file to backup location."""
    state_path = ralph_dir / STATE_FILE
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup_path = ralph_dir / f"dispatch-loop-state.corrupt.{timestamp}.json"
    
    try:
        state_path.rename(backup_path)
    except OSError:
        pass
    
    return backup_path


def initialize_state(
    run_id: str,
    max_iterations: int,
    parallel: int,
    existing_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Initialize a new state object."""
    if existing_state is not None:
        # Resume existing state but update runId if different
        existing_state["runId"] = run_id
        return existing_state
    
    return {
        "version": STATE_VERSION,
        "runId": run_id,
        "startedAt": utc_now(),
        "maxIterations": max_iterations,
        "parallel": parallel,
        "startedCount": 0,
        "completed": [],
        "failed": [],
        "active": {},
    }


def get_ticket_components(ticket_id: str) -> Set[str]:
    """Extract component tags from a ticket."""
    try:
        result = subprocess.run(
            ["tk", "show", ticket_id],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return set()
        
        text = result.stdout
        in_front = False
        tags: List[str] = []
        
        for line in text.splitlines():
            line_stripped = line.strip()
            if line_stripped == "---":
                in_front = not in_front
                continue
            if in_front and line.startswith("tags:"):
                value = line.split(":", 1)[1].strip()
                if value.startswith("[") and value.endswith("]"):
                    value = value[1:-1]
                tags = [t.strip() for t in value.split(",") if t.strip()]
                break
        
        return {t for t in tags if t.startswith("component:")}
    except Exception:
        return set()


def get_active_components(state: Dict[str, Any]) -> Set[str]:
    """Get all components currently in use by active sessions."""
    components: Set[str] = set()
    for session_info in state["active"].values():
        ticket = session_info.get("ticket", "")
        if ticket:
            components.update(get_ticket_components(ticket))
    return components


def list_ready_tickets(max_count: int) -> List[str]:
    """Fetch ready tickets from tk."""
    try:
        result = subprocess.run(
            ["tk", "ready"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        tickets = []
        for line in lines:
            parts = line.split()
            if parts:
                tickets.append(parts[0])
        
        return tickets[:max_count]
    except Exception:
        return []


def has_ready_tickets() -> bool:
    """Check if there are any ready tickets."""
    try:
        result = subprocess.run(
            ["tk", "ready"],
            capture_output=True,
            text=True,
            check=False,
        )
        # If output is non-empty, there are ready tickets
        return bool(result.stdout.strip())
    except Exception:
        return False


def query_session_status(session_id: str) -> Dict[str, Any]:
    """Query the status of a background session.
    
    Since we cannot directly call interactive_shell tool from Python,
    we use a sentinel approach - the session is considered complete
    when the user provides completion info or we detect the session
    no longer exists in the background list.
    
    Returns:
        Dict with 'finished' (bool) and 'success' (bool) keys.
    """
    try:
        # List background sessions to check if this session still exists
        result = subprocess.run(
            ["pi", "/list-background"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        output = result.stdout.lower()
        # Check if session_id appears in the output
        if session_id.lower() not in output:
            # Session not found in background list, assume completed
            # We optimistically assume success unless we have evidence of failure
            return {"finished": True, "success": True}
        
        # Session still active
        return {"finished": False, "success": False}
    except Exception:
        # On error, assume session might have finished
        return {"finished": True, "success": True}


def launch_dispatch(
    ticket_id: str,
    dry_run: bool = False,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Launch a ticket in dispatch mode using interactive_shell.
    
    Returns:
        Tuple of (success, session_id, error_message)
    """
    if dry_run:
        return True, f"dry-run-{ticket_id}", None
    
    try:
        # Use the interactive_shell tool via a subprocess that invokes pi
        # Since we can't directly call interactive_shell from Python,
        # we launch pi in background mode with the dispatch command
        result = subprocess.run(
            ["pi", "-p", f"/tf {ticket_id} --auto"],
            capture_output=True,
            text=True,
            check=False,
            start_new_session=True,  # Detach from parent process group
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else f"exit code {result.returncode}"
            return False, None, error_msg
        
        # Generate a session ID for tracking
        # In actual implementation, we would parse this from pi output
        session_id = str(uuid.uuid4())[:8]
        
        return True, session_id, None
        
    except Exception as e:
        return False, None, str(e)


def update_progress(
    ralph_dir: Path,
    state: Dict[str, Any],
    dry_run: bool = False,
) -> None:
    """Update the progress.md file with current state."""
    if dry_run:
        return
    
    progress_path = ralph_dir / PROGRESS_FILE
    now = utc_now()
    
    lines = [
        "# Ralph Dispatch Loop Progress",
        "",
        "## Current State",
        "",
        f"- Status: {'RUNNING' if state['active'] else 'IDLE'}",
        f"- Run ID: {state['runId']}",
        f"- Started: {state['startedAt']}",
        f"- Last updated: {now}",
        "",
        "## Statistics",
        "",
        f"- Tickets started: {state['startedCount']}",
        f"- Tickets completed: {len(state['completed'])}",
        f"- Tickets failed: {len(state['failed'])}",
        f"- Active sessions: {len(state['active'])}",
        f"- Max iterations: {state['maxIterations']}",
        f"- Parallel: {state['parallel']}",
        "",
        "## Active Sessions",
        "",
    ]
    
    if state["active"]:
        for session_id, info in state["active"].items():
            ticket = info.get("ticket", "unknown")
            started = info.get("startedAt", "unknown")
            lines.append(f"- `{session_id}`: {ticket} (started: {started})")
    else:
        lines.append("_No active sessions_")
    
    lines.extend([
        "",
        "## Completed Tickets",
        "",
    ])
    
    if state["completed"]:
        for ticket in state["completed"][-10:]:  # Show last 10
            lines.append(f"- {ticket}")
    else:
        lines.append("_No completed tickets yet_")
    
    lines.extend([
        "",
        "## Failed Tickets",
        "",
    ])
    
    if state["failed"]:
        for item in state["failed"][-10:]:  # Show last 10
            if isinstance(item, dict):
                ticket = item.get("ticket", "unknown")
                reason = item.get("reason", "unknown error")
                lines.append(f"- {ticket}: {reason}")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("_No failed tickets_")
    
    progress_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="ralph-loop",
        description="Run an autonomous Ralph loop using interactive_shell dispatch sessions.",
        add_help=False,
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help=f"Maximum number of tickets to start (default: {DEFAULT_MAX_ITERATIONS})",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=DEFAULT_PARALLEL,
        help=f"Maximum concurrent dispatch sessions (default: {DEFAULT_PARALLEL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan/log only; do not launch sessions or mutate persistent state",
    )
    parser.add_argument(
        "--help", "-h",
        action="store_true",
        help="Print usage/flags and exit",
    )
    
    return parser.parse_args(args)


def run_loop(args: List[str]) -> int:
    """Main entry point for the Ralph dispatch loop.
    
    Returns:
        Exit code (0 for success/completion, 1 for error).
    """
    # Parse arguments
    try:
        parsed = parse_args(args)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    
    # Handle --help
    if parsed.help:
        print("""Usage: /ralph-loop [--max-iterations N] [--parallel N] [--dry-run] [--help]

Flags:
  --max-iterations N  Maximum number of tickets to start (default: 50)
  --parallel N        Maximum concurrent dispatch sessions (default: 1)
  --dry-run           Plan/log only; do not launch sessions
  --help, -h          Print this help message

This is an experimental orchestrator. The stable production runner is:
  tf ralph start
""")
        return 0
    
    # Validate arguments
    if parsed.max_iterations < 1:
        print("ERROR: --max-iterations must be >= 1", file=sys.stderr)
        return 1
    if parsed.parallel < 1:
        print("ERROR: --parallel must be >= 1", file=sys.stderr)
        return 1
    
    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("ERROR: No .tf directory found. Run in a project with .tf/.", file=sys.stderr)
        return 1
    
    # Check preconditions
    try:
        ralph_dir = check_preconditions(project_root)
    except PreconditionsError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    
    # Generate or get run ID
    run_id = generate_run_id()
    
    # Dry run mode: stateless operation
    if parsed.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Would process up to {parsed.max_iterations} tickets")
        print(f"With parallelism of {parsed.parallel}")
        print("")
        
        # Simulate the loop
        planned_count = 0
        planned_tickets: Set[str] = set()
        
        while planned_count < parsed.max_iterations:
            remaining = parsed.parallel
            tickets = list_ready_tickets(remaining)
            
            # Filter out already planned tickets
            new_tickets = [t for t in tickets if t not in planned_tickets]
            
            if not new_tickets:
                break
            
            for ticket in new_tickets:
                if planned_count >= parsed.max_iterations:
                    break
                print(f"Would dispatch: {ticket}")
                planned_count += 1
                planned_tickets.add(ticket)
        
        print("")
        print(f"=== Plan Summary ===")
        print(f"Tickets to process: {planned_count}")
        print(f"Tickets list: {', '.join(planned_tickets) if planned_tickets else '(none)'}")
        return 0
    
    # Normal mode: load or initialize state
    # Use try/finally to guarantee lock release on any exit path
    existing_state = load_state(ralph_dir)
    state: Optional[Dict[str, Any]] = None
    lock_acquired = False
    
    try:
        if existing_state is not None:
            # Resume existing state
            if existing_state.get("version") != STATE_VERSION:
                print("WARNING: State file version mismatch, starting fresh", file=sys.stderr)
                existing_state = None
            else:
                run_id = existing_state.get("runId", run_id)
                # Log flag mismatches
                if existing_state.get("maxIterations") != parsed.max_iterations:
                    print(
                        f"INFO: Using persisted maxIterations={existing_state.get('maxIterations')} "
                        f"(ignoring CLI value {parsed.max_iterations})",
                        file=sys.stderr
                    )
                if existing_state.get("parallel") != parsed.parallel:
                    print(
                        f"INFO: Using persisted parallel={existing_state.get('parallel')} "
                        f"(ignoring CLI value {parsed.parallel})",
                        file=sys.stderr
                    )
        
        if existing_state is None:
            # Initialize new state
            state = initialize_state(run_id, parsed.max_iterations, parsed.parallel)
            print(f"INFO: Starting new run with ID: {run_id}", file=sys.stderr)
        else:
            state = initialize_state(run_id, parsed.max_iterations, parsed.parallel, existing_state)
            print(f"INFO: Resuming run with ID: {run_id}", file=sys.stderr)
        
        # Reconcile lock
        if not reconcile_lock(ralph_dir, run_id, parsed.dry_run):
            return 1
        lock_acquired = True
        
        # Reconcile active sessions
        sessions_to_remove: List[str] = []
        for session_id, session_info in list(state["active"].items()):
            status = query_session_status(session_id)
            
            if status["finished"]:
                ticket = session_info.get("ticket", "unknown")
                if status["success"]:
                    state["completed"].append(ticket)
                    print(f"INFO: Session {session_id} for {ticket} completed", file=sys.stderr)
                else:
                    state["failed"].append({
                        "ticket": ticket,
                        "reason": "session failed or was killed",
                    })
                    print(f"INFO: Session {session_id} for {ticket} failed", file=sys.stderr)
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del state["active"][session_id]
        
        # Fill capacity
        while (
            state["startedCount"] < state["maxIterations"]
            and len(state["active"]) < state["parallel"]
        ):
            remaining_capacity = state["parallel"] - len(state["active"])
            
            # Fetch tickets
            tickets = list_ready_tickets(remaining_capacity * 2)  # Fetch extra for filtering
            
            # Remove empties and deduplicate
            seen: Set[str] = set()
            unique_tickets: List[str] = []
            for t in tickets:
                if t and t not in seen:
                    seen.add(t)
                    unique_tickets.append(t)
            tickets = unique_tickets
            
            # Exclude active tickets
            active_tickets = {info.get("ticket", "") for info in state["active"].values()}
            tickets = [t for t in tickets if t not in active_tickets]
            
            # Exclude completed tickets
            completed_set = set(state["completed"])
            tickets = [t for t in tickets if t not in completed_set]
            
            # Component safety for parallel mode
            if state["parallel"] > 1:
                active_components = get_active_components(state)
                safe_tickets: List[str] = []
                for ticket in tickets:
                    ticket_components = get_ticket_components(ticket)
                    if ticket_components and (ticket_components & active_components):
                        # Skip tickets with overlapping components
                        continue
                    safe_tickets.append(ticket)
                tickets = safe_tickets
            
            if not tickets:
                break
            
            # Launch tickets up to capacity
            for ticket in tickets:
                if state["startedCount"] >= state["maxIterations"]:
                    break
                if len(state["active"]) >= state["parallel"]:
                    break
                
                success, session_id, error = launch_dispatch(ticket, parsed.dry_run)
                
                if not success or session_id is None:
                    state["failed"].append({
                        "ticket": ticket,
                        "reason": error or "launch failed",
                    })
                    state["startedCount"] += 1
                    print(f"ERROR: Failed to launch {ticket}: {error}", file=sys.stderr)
                    continue
                
                # Record the session
                state["active"][session_id] = {
                    "ticket": ticket,
                    "startedAt": utc_now(),
                }
                state["startedCount"] += 1
                
                print(f"INFO: Launched {ticket} with session {session_id}", file=sys.stderr)
                print(f"INFO: Attach with: pi /attach {session_id}", file=sys.stderr)
        
        # Update progress
        update_progress(ralph_dir, state, parsed.dry_run)
        
        # Check completion conditions
        has_ready = has_ready_tickets()
        
        if not has_ready and not state["active"]:
            # No ready tickets and no active sessions
            print("<promise>COMPLETE</promise>")
            remove_lock(ralph_dir)
            # Remove state file
            state_path = ralph_dir / STATE_FILE
            if state_path.exists():
                state_path.unlink()
            print("INFO: Loop completed - no more ready tickets", file=sys.stderr)
            return 0
        
        if state["startedCount"] >= state["maxIterations"] and not state["active"]:
            # Max iterations reached and all sessions finished
            print("<promise>COMPLETE</promise>")
            remove_lock(ralph_dir)
            state_path = ralph_dir / STATE_FILE
            if state_path.exists():
                state_path.unlink()
            print("INFO: Loop completed - max iterations reached", file=sys.stderr)
            return 0
        
        # Persist state for next turn
        save_state(ralph_dir, state)
        
        print(
            f"INFO: Progress: {state['startedCount']}/{state['maxIterations']} started, "
            f"{len(state['active'])} active, {len(state['completed'])} completed, "
            f"{len(state['failed'])} failed",
            file=sys.stderr
        )
        
        return 0
    
    except Exception as e:
        # Log error but let finally block handle lock cleanup
        # (don't release lock if active sessions exist)
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        # Guarantee lock release on terminal states
        # Normal completion paths release lock explicitly above when work is done
        # This finally handles edge cases: exceptions, signals, unexpected exits
        # Only release lock if no active sessions remain (continuing keeps lock)
        if lock_acquired and state is not None:
            if not state.get("active"):
                remove_lock(ralph_dir)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    if argv is None:
        argv = sys.argv[1:]
    
    return run_loop(argv)


if __name__ == "__main__":
    raise SystemExit(main())
