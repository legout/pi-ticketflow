---
id: pt-7jzy
status: closed
deps: [pt-9yjn]
links: [pt-9yjn, pt-699h]
created: 2026-02-13T16:05:22Z
closed: 2026-02-14T00:11:41Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-ralph-loop-background-interactive
tags: [tf, backlog, component:cli, component:workflow]
---
# Handle dispatch completion and graceful session termination

## Task
Implement completion handling that treats session exit as authoritative and applies EOF/kill fallback when needed.

## Context
The plan resolves completion to session lifecycle events rather than fragile output parsing.
If a session idles after workflow completion, Ralph must close it safely.

## Acceptance Criteria
- [x] Completion is detected from dispatch/session state.
- [x] Idle sessions receive graceful EOF (`Ctrl+D`) before forced kill.
- [x] Timeout and forced termination outcomes are reported in progress/logs.

## Constraints
- Ensure no orphan processes remain after timeout paths.

## Implementation Summary

### New Module: `tf/ralph_completion.py`

Added completion handling functions:

- **`poll_dispatch_status(pid)`**: Non-blocking process status check using `os.waitpid(WNOHANG)`
- **`graceful_terminate_dispatch(pid, ...)`**: Graceful termination with SIGTERM → wait → SIGKILL sequence
- **`wait_for_dispatch_completion(dispatch_result, ...)`**: Main monitoring function with timeout and reporting
- **`cleanup_dispatch_tracking(ralph_dir, ticket)`**: Cleanup tracking files after completion
- **`update_dispatch_tracking_status(...)`**: Update tracking file with completion status

### Key Types

- `DispatchCompletionStatus` enum: RUNNING, COMPLETED, TIMEOUT, TERMINATED, ERROR
- `DispatchCompletionResult` dataclass: Captures final status, return code, duration, termination method

### Modified: `tf/ralph/__init__.py`

Added exports for:
- `DispatchResult` and `run_ticket_dispatch` (from ralph.py)
- All completion handling functions from `ralph_completion.py`

## Usage Example

```python
from tf.ralph import run_ticket_dispatch, wait_for_dispatch_completion

# Launch dispatch
dispatch_result = run_ticket_dispatch(ticket="pt-123", ...)

# Wait for completion with timeout
completion = wait_for_dispatch_completion(
    dispatch_result=dispatch_result,
    ticket_id="pt-123",
    timeout_ms=600000,
    logger=logger,
)

# Handle result
if completion.status == DispatchCompletionStatus.COMPLETED:
    print(f"Success! Duration: {completion.duration_ms}ms")
elif completion.status == DispatchCompletionStatus.TIMEOUT:
    print(f"Terminated via: {completion.termination_method}")
```

## References
- Seed: seed-add-ralph-loop-background-interactive
- Plan: plan-ralph-background-interactive-shell
- Spike: spike-interactive-shell-execution
