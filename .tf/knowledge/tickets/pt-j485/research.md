# Research: pt-j485 - Ensure cleanup semantics after timeout

## Ticket Analysis
Ticket pt-j485 ensures cleanup semantics when timeouts occur, including:
- Worktrees (parallel mode)
- Lock files
- Progress state updates

## Codebase Review

### Current Timeout Implementation (Serial Mode)
- `attemptTimeoutMs` config (default 600000ms = 10min)
- `maxRestarts` config (default 0 = no restarts)
- `_run_with_timeout()` function handles subprocess termination:
  1. Try graceful termination (SIGTERM)
  2. Wait 5 seconds
  3. Force kill (SIGKILL) if needed
  4. Wait to reap process (prevents zombies)
  5. Returns (-1, True) for timeout

### Serial Mode Cleanup (CORRECT ✓)
- Lock: Acquired at start, released in `finally` block ✓
- Progress: Updated via `update_state()` with timeout error message ✓
- State reflects: "FAILED" with "timed out after X attempt(s)" message ✓

### Parallel Mode Issues (NEEDS FIX ✗)
- **NO timeout handling** - uses bare `subprocess.Popen` without timeout
- **NO restart logic** - no equivalent of serial mode's bounded restart loop
- **Worktree cleanup**: Only happens on process completion, not timeout
- **Risk**: Timeout config is silently ignored in parallel mode

### Constraint Compliance
Per ticket constraints: "Prefer warn+disable in parallel mode over partial/unsafe behavior"

## Required Changes

1. **Parallel mode timeout detection**: Add timeout handling to parallel worktree processing
2. **Warn+disable strategy**: When timeout is configured and parallel mode is requested, warn user and fall back to serial
3. **Documentation**: Update config comments to clarify timeout only works in serial mode

## Files to Modify
- `tf_cli/ralph.py` - Add parallel mode timeout safety
