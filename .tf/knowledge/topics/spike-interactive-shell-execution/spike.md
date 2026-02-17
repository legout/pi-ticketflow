# Spike: Interactive Shell Execution for Ralph

## Overview
Research how to execute Ralph ticket implementations using background `interactive_shell` sessions instead of the current `pi -p` subprocess approach.

## Current Implementation

```python
# Ralph uses pi -p (batch/non-interactive mode)
args = ["pi", "-p"]
if capture_json:
    args.extend(["--mode", "json"])
args.append(cmd)  # e.g., "/tf ticket-123 --auto"

# With timeout handling via subprocess
return_code, timed_out = _run_with_timeout(args, cwd=cwd, timeout_secs=timeout_secs)
```

## Proposal: Background Interactive Shell

```python
# Instead: use interactive_shell with background dispatch
interactive_shell({
    command: 'pi /tf {ticket_id} --auto',
    mode: "dispatch",  # or "background"
    background: true
})
```

## Research Questions

### 1. Completion Detection

**Q**: How does Ralph know when `pi /tf --auto` is done in a background shell?

**Options**:
- Monitor for promise sigil `<promise>...` in output
- Wait for session to exit (notification via triggerTurn)
- Poll session status periodically

**Current Ralph behavior**: Checks for `<promise>` in subprocess output.

**Recommendation**: Use dispatch mode with `triggerTurn` notification. The session exit is the completion signal.

### 2. Auto-Exit Mechanism

**Q**: How does pi exit when `/tf` completes?

**Current behavior**: `pi -p` exits automatically when prompt completes.

**Interactive mode**: `pi /tf` waits for more input after workflow finishes.

**Solution**: Send `exit` or EOF (`Ctrl+D`) after detecting completion. However, with `--auto` flag, pi should exit automatically when the workflow signals completion.

**Verification needed**: Does `/tf --auto` cause pi to exit automatically?

### 3. Session Lifecycle

| Phase | Current (subprocess) | Proposed (interactive_shell) |
|-------|---------------------|------------------------------|
| Start | `pi -p /tf ticket` | `interactive_shell(command: 'pi /tf ticket --auto')` |
| Run | Block until done | Non-blocking, monitored |
| Complete | Return code | Notification + output capture |
| Cleanup | Process terminates | Session closes |

### 4. Parallel Execution

**Current Ralph parallel**: Uses git worktrees for isolation.

**Proposed**: Multiple `interactive_shell` background sessions can run concurrently:
- Each ticket gets its own session
- No worktree needed (fresh process per ticket)
- Component tags still used for dependency coordination

**Benefits**:
- Simpler than worktrees
- Faster (no git operations)
- Fresh context per ticket guaranteed

### 5. Monitoring & Observability

**User visibility**:
- `interactive_shell({ sessionId: "xxx", attach: "xxx" })` to watch live
- Query output via `interactive_shell({ sessionId: "xxx" })`
- Background sessions don't show overlay by default

**Ralph progress tracking**:
- Progress file still updated after each ticket
- Lessons extracted from session output

## Key Code References

- `tf/ralph.py:462-570` - `run_ticket()` function
- `tf/ralph.py:393-416` - `build_cmd()` function
- `interactive_shell` skill - dispatch/background modes

## Open Questions

1. Does `pi /tf ticket --auto` exit automatically when workflow completes?
2. What is the exact output pattern when `/tf` finishes?
3. How to handle stuck/hanging sessions (timeout + kill)?
4. Should finished sessions be retained for debugging (vs auto-cleanup)?

## Next Steps

1. **Prototype**: Test `pi /tf <ticket-id> --auto` in background dispatch mode
2. **Verify completion signal**: Confirm promise sigil or exit behavior
3. **Implement loop**: Wire background sessions into Ralph orchestration
4. **Add parallel support**: Coordinate multiple concurrent sessions
