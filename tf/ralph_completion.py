"""Dispatch session completion handling for Ralph.

This module provides functions for monitoring and gracefully terminating
dispatch sessions, including EOF-based graceful shutdown and timeout handling.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from tf.logger import LogLevel, RalphLogger, create_logger


class DispatchCompletionStatus(Enum):
    """Status of a dispatch session completion check."""
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    TERMINATED = "terminated"
    ERROR = "error"


@dataclass
class DispatchCompletionResult:
    """Result of waiting for a dispatch session to complete.
    
    Attributes:
        ticket_id: The ticket ID that was being processed
        session_id: The session ID of the dispatch
        status: Final completion status
        return_code: Exit code of the process (if completed normally)
        pid: Process ID that was monitored
        duration_ms: Total time waited in milliseconds
        termination_method: How the process was terminated:
            - "natural": Process exited on its own
            - "sigterm": Process terminated by SIGTERM
            - "sigkill": Process killed by SIGKILL
            - "not_running": Process was already stopped
            - "failed": Termination attempt failed
        error: Error message if something went wrong
    """
    ticket_id: str
    session_id: str
    status: DispatchCompletionStatus
    return_code: Optional[int] = None
    pid: Optional[int] = None
    duration_ms: float = 0.0
    termination_method: str = "natural"
    error: Optional[str] = None


def poll_dispatch_status(pid: int) -> tuple[bool, Optional[int]]:
    """Poll the status of a dispatch process.
    
    Uses waitpid with WNOHANG to check status without blocking. This avoids
    race conditions by using a single syscall for both existence check and
    status retrieval.
    
    Args:
        pid: Process ID to check
        
    Returns:
        Tuple of (is_running, return_code)
        - is_running: True if process is still running
        - return_code: Exit code if process has completed, None if still running
    """
    try:
        # Use waitpid with WNOHANG to check without blocking
        # This returns (ret_pid, status) where:
        # - ret_pid == 0 means process is still running
        # - ret_pid == pid means process has exited and we have its status
        ret_pid, status = os.waitpid(pid, os.WNOHANG)
        
        if ret_pid == 0:
            # Process still running (no status change)
            return True, None
        else:
            # Process has exited (ret_pid == pid)
            if os.WIFEXITED(status):
                return False, os.WEXITSTATUS(status)
            elif os.WIFSIGNALED(status):
                return False, -os.WTERMSIG(status)
            else:
                return False, None
    except ChildProcessError:
        # Process does not exist (already exited and reaped, or not our child)
        return False, None
    except Exception:
        # On other errors, assume process has exited
        return False, None


def graceful_terminate_dispatch(
    pid: int,
    session_id: Optional[str] = None,
    logger: Optional[RalphLogger] = None,
    kill_wait_ms: float = 5000.0,
    use_process_group: bool = True,
) -> tuple[bool, str]:
    """Gracefully terminate a dispatch process.
    
    Sends SIGTERM for graceful shutdown, then SIGKILL if the process
    does not terminate within the wait period.
    
    Note: EOF (Ctrl+D) signaling is not implemented for subprocess processes
    that have already been launched. The termination sequence goes directly
    from SIGTERM to SIGKILL.
    
    Args:
        pid: Process ID to terminate
        session_id: Optional session ID for logging
        logger: Optional logger instance
        kill_wait_ms: Milliseconds to wait after SIGTERM before SIGKILL
        use_process_group: If True, send signals to the process group (-pid) to
            ensure child processes are also terminated. Should be True when the
            dispatch was started with start_new_session=True.
        
    Returns:
        Tuple of (success, method_used)
        - success: True if process was terminated
        - method_used: "sigterm", "sigkill", "not_running", or "failed"
    """
    log = logger or create_logger(level=LogLevel.NORMAL)
    
    # First check if process is still running
    is_running, _ = poll_dispatch_status(pid)
    if not is_running:
        if logger:
            logger.debug(f"Process {pid} already exited")
        return True, "not_running"
    
    # Log the graceful termination attempt
    if session_id:
        log.info(f"Attempting graceful termination for session {session_id} (PID: {pid})")
    else:
        log.info(f"Attempting graceful termination for PID: {pid}")
    
    # Determine target for signals: process group (-pid) or single process (pid)
    # Using -pid sends the signal to the entire process group
    target = -pid if use_process_group else pid
    target_desc = f"process group {pid}" if use_process_group else f"PID {pid}"
    
    # Step 1: Send SIGTERM for graceful shutdown
    try:
        if use_process_group:
            os.killpg(target, signal.SIGTERM)
        else:
            os.kill(target, signal.SIGTERM)
        if logger:
            logger.debug(f"Sent SIGTERM to {target_desc}")
    except ProcessLookupError:
        # Process already exited
        return True, "not_running"
    except OSError as e:
        # Process group may not exist (process not in a group or already dead)
        if logger:
            logger.warning(f"Failed to send SIGTERM to {target_desc}: {e}")
        # Fall back to single process
        try:
            os.kill(pid, signal.SIGTERM)
            if logger:
                logger.debug(f"Sent SIGTERM to PID {pid} (fallback)")
        except ProcessLookupError:
            return True, "not_running"
        except Exception as e2:
            if logger:
                logger.warning(f"Failed to send SIGTERM to PID {pid}: {e2}")
    
    # Wait for graceful shutdown
    wait_start = time.time()
    wait_end = wait_start + (kill_wait_ms / 1000.0)
    
    while time.time() < wait_end:
        is_running, _ = poll_dispatch_status(pid)
        if not is_running:
            elapsed_ms = (time.time() - wait_start) * 1000
            if logger:
                logger.debug(f"Process {pid} terminated gracefully after {elapsed_ms:.0f}ms")
            return True, "sigterm"
        time.sleep(0.1)  # 100ms polling interval
    
    # Step 2: Process still running, send SIGKILL
    if logger:
        logger.warning(f"Process {pid} did not terminate after {kill_wait_ms}ms, sending SIGKILL")
    
    try:
        if use_process_group:
            os.killpg(target, signal.SIGKILL)
        else:
            os.kill(target, signal.SIGKILL)
        if logger:
            logger.debug(f"Sent SIGKILL to {target_desc}")
    except ProcessLookupError:
        # Process exited between poll and kill
        return True, "sigterm"
    except OSError:
        # Fall back to single process
        try:
            os.kill(pid, signal.SIGKILL)
            if logger:
                logger.debug(f"Sent SIGKILL to PID {pid} (fallback)")
        except ProcessLookupError:
            return True, "sigterm"
        except Exception as e:
            if logger:
                logger.error(f"Failed to send SIGKILL to PID {pid}: {e}")
            return False, "failed"
    except Exception as e:
        if logger:
            logger.error(f"Failed to send SIGKILL to {target_desc}: {e}")
        return False, "failed"
    
    # Wait for process to be reaped after SIGKILL
    kill_wait_start = time.time()
    kill_wait_end = kill_wait_start + 2.0  # 2 second max wait after SIGKILL
    
    while time.time() < kill_wait_end:
        is_running, _ = poll_dispatch_status(pid)
        if not is_running:
            return True, "sigkill"
        time.sleep(0.05)  # 50ms polling after SIGKILL
    
    # Process still exists after SIGKILL - this is unusual (possibly D-state)
    if logger:
        logger.error(f"Process {pid} still exists after SIGKILL (may be in uninterruptible sleep)")
    return False, "failed"


def wait_for_dispatch_completion(
    dispatch_result: Any,  # DispatchResult
    ticket_id: str,
    timeout_ms: int = 0,
    poll_interval_ms: float = 1000.0,
    logger: Optional[RalphLogger] = None,
    graceful_shutdown_ms: float = 5000.0,
) -> DispatchCompletionResult:
    """Wait for a dispatch session to complete with timeout and graceful termination.
    
    This function monitors a dispatch session until it completes, times out, or
    is terminated. It provides graceful shutdown semantics (SIGTERM before SIGKILL).
    
    Args:
        dispatch_result: The DispatchResult from run_ticket_dispatch
        ticket_id: Ticket ID being processed
        timeout_ms: Maximum time to wait in milliseconds (0 = no timeout)
        poll_interval_ms: How often to poll for status in milliseconds
        logger: Optional logger instance
        graceful_shutdown_ms: Time to wait for graceful shutdown before forced kill
        
    Returns:
        DispatchCompletionResult with final status and termination details
    """
    log = logger or create_logger(level=LogLevel.NORMAL, ticket_id=ticket_id)
    
    session_id = dispatch_result.session_id
    pid = dispatch_result.pid
    
    if not pid:
        error_msg = "Cannot wait for completion: no PID in dispatch result"
        log.error(error_msg, ticket=ticket_id)
        return DispatchCompletionResult(
            ticket_id=ticket_id,
            session_id=session_id,
            status=DispatchCompletionStatus.ERROR,
            error=error_msg,
        )
    
    log.info(f"Waiting for dispatch completion: session={session_id}, pid={pid}", ticket=ticket_id)
    
    start_time = time.time()
    timeout_sec = timeout_ms / 1000.0 if timeout_ms > 0 else None
    poll_interval_sec = poll_interval_ms / 1000.0
    
    last_log_time = start_time
    log_interval_sec = 30.0  # Log progress every 30 seconds
    
    while True:
        current_time = time.time()
        elapsed_sec = current_time - start_time
        elapsed_ms = elapsed_sec * 1000
        
        # Check if we've exceeded timeout
        if timeout_sec and elapsed_sec >= timeout_sec:
            log.warn(f"Dispatch timeout after {timeout_ms}ms, initiating graceful termination", ticket=ticket_id)
            
            # Attempt graceful termination
            terminated, method = graceful_terminate_dispatch(
                pid=pid,
                session_id=session_id,
                logger=log,
                kill_wait_ms=graceful_shutdown_ms,
            )
            
            final_duration_ms = (time.time() - start_time) * 1000
            
            if terminated:
                return DispatchCompletionResult(
                    ticket_id=ticket_id,
                    session_id=session_id,
                    status=DispatchCompletionStatus.TIMEOUT,
                    pid=pid,
                    duration_ms=final_duration_ms,
                    termination_method=method,
                    error=f"Timeout after {timeout_ms}ms",
                )
            else:
                return DispatchCompletionResult(
                    ticket_id=ticket_id,
                    session_id=session_id,
                    status=DispatchCompletionStatus.ERROR,
                    pid=pid,
                    duration_ms=final_duration_ms,
                    termination_method=method,
                    error=f"Failed to terminate process after timeout",
                )
        
        # Check process status
        is_running, return_code = poll_dispatch_status(pid)
        
        if not is_running:
            # Process has completed
            final_duration_ms = (time.time() - start_time) * 1000
            
            if return_code is not None and return_code == 0:
                log.info(
                    f"Dispatch completed successfully in {final_duration_ms:.0f}ms (exit: 0)",
                    ticket=ticket_id
                )
                return DispatchCompletionResult(
                    ticket_id=ticket_id,
                    session_id=session_id,
                    status=DispatchCompletionStatus.COMPLETED,
                    return_code=return_code,
                    pid=pid,
                    duration_ms=final_duration_ms,
                    termination_method="natural",
                )
            elif return_code is not None:
                log.warn(
                    f"Dispatch failed after {final_duration_ms:.0f}ms (exit: {return_code})",
                    ticket=ticket_id
                )
                return DispatchCompletionResult(
                    ticket_id=ticket_id,
                    session_id=session_id,
                    status=DispatchCompletionStatus.ERROR,
                    return_code=return_code,
                    pid=pid,
                    duration_ms=final_duration_ms,
                    termination_method="natural",
                    error=f"Process exited with code {return_code}",
                )
            else:
                # Process exited but we couldn't get return code
                log.info(f"Dispatch completed (unknown exit code) after {final_duration_ms:.0f}ms", ticket=ticket_id)
                return DispatchCompletionResult(
                    ticket_id=ticket_id,
                    session_id=session_id,
                    status=DispatchCompletionStatus.COMPLETED,
                    pid=pid,
                    duration_ms=final_duration_ms,
                    termination_method="natural",
                )
        
        # Log progress periodically
        if current_time - last_log_time >= log_interval_sec:
            log.info(f"Dispatch still running after {elapsed_ms/1000:.0f}s...", ticket=ticket_id)
            last_log_time = current_time
        
        # Sleep before next poll
        time.sleep(poll_interval_sec)


def cleanup_dispatch_tracking(ralph_dir: Path, ticket: str, logger: Optional[RalphLogger] = None) -> None:
    """Clean up dispatch tracking file after session completion.
    
    Args:
        ralph_dir: Ralph directory path
        ticket: Ticket ID
        logger: Optional logger
    """
    tracking_file = ralph_dir / "dispatch" / f"{ticket}.json"
    if tracking_file.exists():
        try:
            tracking_file.unlink()
            if logger:
                logger.debug(f"Cleaned up dispatch tracking file: {tracking_file}", ticket=ticket)
        except Exception as e:
            if logger:
                logger.warning(f"Failed to clean up tracking file: {e}", ticket=ticket)


def update_dispatch_tracking_status(
    ralph_dir: Path,
    ticket: str,
    completion_result: DispatchCompletionResult,
    logger: Optional[RalphLogger] = None,
) -> None:
    """Update dispatch tracking file with completion status.
    
    Args:
        ralph_dir: Ralph directory path
        ticket: Ticket ID
        completion_result: The completion result
        logger: Optional logger
    """
    import json
    
    tracking_file = ralph_dir / "dispatch" / f"{ticket}.json"
    if not tracking_file.exists():
        return
    
    try:
        data = json.loads(tracking_file.read_text(encoding="utf-8"))
        data["status"] = completion_result.status.value
        data["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        data["return_code"] = completion_result.return_code
        data["duration_ms"] = completion_result.duration_ms
        data["termination_method"] = completion_result.termination_method
        if completion_result.error:
            data["error"] = completion_result.error
        
        tracking_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        if logger:
            logger.debug(f"Updated dispatch tracking file with completion status", ticket=ticket)
    except Exception as e:
        if logger:
            logger.warning(f"Failed to update tracking file: {e}", ticket=ticket)

