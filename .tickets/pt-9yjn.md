---
id: pt-9yjn
status: closed
deps: [pt-0v53]
links: [pt-0v53, pt-7jzy]
created: 2026-02-13T16:05:22Z
closed: 2026-02-13T23:51:00Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-ralph-loop-background-interactive
tags: [tf, backlog, component:cli, component:workflow]
---
# Implement run_ticket_dispatch launcher for Ralph

## Task
Implement a dispatch-based ticket runner that launches `pi /tf <ticket> --auto` in background sessions.

## Context
Current Ralph uses `pi -p` subprocess execution in `run_ticket()`.
The new backend should create one isolated Pi session per ticket for fresh context.

## Acceptance Criteria
- [x] New runner launches one interactive_shell dispatch session per ticket.
- [x] Session ID and ticket ID are captured together for tracking.
- [x] Runner returns structured result for success/failure handling.

## Implementation Summary

### Changes Made
- **tf/ralph.py**: Added `DispatchResult` dataclass and `run_ticket_dispatch()` function
  - Returns structured `DispatchResult` with `session_id`, `ticket_id`, `success`, `return_code`, and `error_message`
  - Supports all same parameters as `run_ticket()` for API compatibility
  - Generates unique session IDs for tracking (format: `ralph-{ticket}-{uuid}`)
  - Includes dry-run mode support
  - Proper validation (ticket exists, pi in PATH, /tf prompt exists)

- **tf/ralph/__init__.py**: Exported new `run_ticket_dispatch` function and `DispatchResult` class

### Usage
```python
from tf.ralph import run_ticket_dispatch, DispatchResult

result = run_ticket_dispatch(
    ticket="pt-123",
    workflow="/tf",
    flags="--auto",
    dry_run=False,
)
# result.session_id = "ralph-pt-123-a1b2c3d4"
# result.ticket_id = "pt-123"
# result.success = True
# result.return_code = 0
```

## Constraints
- Avoid changing ticket workflow semantics beyond execution transport.

## References
- Seed: seed-add-ralph-loop-background-interactive
- Plan: plan-ralph-background-interactive-shell
- Spike: spike-interactive-shell-execution

