# Research: pt-uu03

## Status
Research completed. Internal codebase and skill documentation reviewed. No external research needed - this is a manual validation ticket for existing implementation.

## Rationale
This ticket is a **manual validation task** for the dispatch Ralph mode implementation. Research focused on understanding:
1. The current dispatch implementation in `tf/ralph.py`
2. The interactive_shell skill capabilities and modes
3. The planned validation scenarios from the seed/spike/plan documents

No external research was required as this ticket validates internal functionality.

## Context Reviewed

### 1. Ticket Details (`tk show pt-uu03`)
- **Type**: Task
- **Purpose**: Execute and document manual validation scenarios
- **Acceptance Criteria**:
  - [ ] Serial dispatch run validated end-to-end
  - [ ] Parallel dispatch run validated with non-overlapping component tags
  - [ ] Fallback `--no-interactive-shell` path validated
  - [ ] Timeout/orphan recovery scenarios validated and logged
- **Dependencies**: Blocked by pt-4eor (integrate dispatch backend)
- **Linked**: pt-8qk8 (orphaned session recovery - closed), pt-4eor (dispatch backend integration - open)

### 2. Knowledge Topics

#### Seed: `seed-add-ralph-loop-background-interactive`
**Vision**: Ralph supports background interactive Pi processes per ticket with live observability.

Key features:
- Fresh context per ticket (isolated Pi sessions)
- Background autonomy via dispatch mode
- Live observability on demand via `/attach`
- Parallel workers with component/dependency safeguards
- State continuity via progress.md and AGENTS.md

#### Spike: `spike-interactive-shell-execution`
**Research findings** on `interactive_shell` integration:

| Aspect | Finding |
|--------|---------|
| Completion Detection | Dispatch mode with `triggerTurn` notification; session exit as authoritative signal |
| Auto-Exit | `--auto` flag causes pi to exit automatically when workflow completes |
| Session Lifecycle | Non-blocking launch, poll/wait for completion, cleanup on finish |
| Parallel Execution | Multiple `interactive_shell` background sessions can run concurrently |
| Benefits over worktrees | Simpler, faster (no git ops), fresh context guaranteed |

Open questions from spike (now addressed in plan):
1. ✅ `pi /tf --auto` exit behavior confirmed
2. ✅ Completion signal: session lifecycle completion preferred over text parsing
3. ✅ Timeout handling: kill after threshold
4. ✅ Session retention: TTL-based cleanup

#### Plan: `plan-ralph-background-interactive-shell` (APPROVED)
**Implementation phases**:

**Phase 1: Foundation (MVP)**
- `run_ticket_dispatch()` function using subprocess.Popen
- `--dispatch` flag (default enabled), `--no-interactive-shell` fallback
- Worktree management per ticket
- Progress and lessons extraction

**Phase 2: Parallel Support**
- Multiple concurrent session tracking
- Component tag-based dependency safety

**Phase 3: Observability**
- User attachment commands
- Session output capture

**Phase 4: Reliability**
- Timeout handling
- Orphaned session cleanup

### 3. Implementation Code (`tf/ralph.py`)

#### Current Dispatch Implementation
```python
def run_ticket_dispatch(...)
    # Uses subprocess.Popen to launch 'pi -p /tf <ticket> --auto'
    # Returns immediately with session_id and pid
    # Registers session for recovery tracking (pt-8qk8)
```

Key implementation details:
- Uses `subprocess.Popen` with `start_new_session=True` for process group isolation
- Session tracking via `_dispatch_active_session_ids` (in-process) + session_recovery module (persistent)
- Signal handlers installed to cleanup children on SIGINT/SIGTERM
- Log file output support for debugging
- Health check immediately after launch to catch startup failures

#### Session Recovery (pt-8qk8 - CLOSED)
```python
from tf.ralph.session_recovery import (
    register_dispatch_session,
    remove_dispatch_session,
    run_startup_recovery,
    update_dispatch_session_status,
)
```
- Persistent session state in `.tf/ralph/dispatch-sessions.json` (single JSON array, not JSONL)
- TTL-based cleanup (default: 24 hours)
- Startup recovery for orphaned sessions from previous Ralph runs

### 4. Interactive Shell Skill (`~/.pi/agent/skills/interactive-shell/SKILL.md`)

**Tool**: `interactive_shell` with dispatch mode

| Mode | Use Case | Blocking |
|------|----------|----------|
| `dispatch` | Fire-and-forget, notified on completion | No |
| `hands-free` | Monitor with periodic status queries | No |
| `interactive` | User supervises and can intervene | Yes |

**Background dispatch (headless)**:
```typescript
interactive_shell({
  command: 'pi "Fix lint errors"',
  mode: "dispatch",
  background: true
})
```

**Key capabilities**:
- Session ID tracking for status queries
- `attach` to running sessions for live observation
- `listBackground` / `dismissBackground` for session management
- Input injection (`input`, `inputKeys`, `inputPaste`)
- Configurable update intervals and quiet thresholds

## Validation Scenarios Required

Based on acceptance criteria and implementation review:

### 1. Serial Dispatch Validation
**Command**: `tf ralph run <ticket> --dispatch`
**Verify**:
- Ticket executes in dispatched subprocess
- Fresh Pi context (no context bleed)
- Session ID assigned and logged
- Worktree created on start, merged on close
- Progress updated after completion
- Lessons extracted to AGENTS.md

### 2. Parallel Dispatch Validation
**Command**: `tf ralph start --parallel 3 --dispatch`
**Verify**:
- Multiple tickets run concurrently
- Component tag isolation respected (non-overlapping components)
- Dependency ordering maintained (blocked tickets wait)
- Each ticket has independent session
- Mixed success/failure handled correctly

### 3. Fallback Path Validation
**Command**: `tf ralph run <ticket> --no-interactive-shell`
**Verify**:
- Falls back to original subprocess implementation
- No interactive_shell tool invocation
- Same progress/lessons semantics
- Backward compatibility maintained

### 4. Timeout/Orphan Recovery Validation
**Command**: Various stress scenarios
**Verify**:
- Stuck sessions detected after timeout threshold
- Sessions killed gracefully (SIGTERM → SIGKILL)
- Orphaned sessions from previous Ralph runs recovered on startup
- TTL cleanup removes stale session records
- Process group termination works correctly

## Test Notes Guidelines

Per ticket constraints: "Keep test notes concise and reproducible by other contributors."

**Template for each scenario**:
```markdown
## Scenario: <Name>
Date: YYYY-MM-DD
Command: <exact command>
Ticket(s): <ticket-id(s)>

### Expected
- <criteria 1>
- <criteria 2>

### Observed
- <observation 1>
- <observation 2>

### Result
PASS / FAIL

### Notes
<Any anomalies or follow-up needed>
```

## Sources

1. **Ticket**: `tk show pt-uu03` - Task definition and acceptance criteria
2. **Seed**: `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/seed.md` - Vision and core concept
3. **Spike**: `.tf/knowledge/topics/spike-interactive-shell-execution/spike.md` - Research findings and questions
4. **Plan**: `.tf/knowledge/topics/plan-ralph-background-interactive-shell/plan.md` - Approved implementation plan
5. **Code**: `tf/ralph.py:806-1106` - `run_ticket_dispatch()` implementation
6. **Skill**: `~/.pi/agent/skills/interactive-shell/SKILL.md` - Tool documentation and usage patterns
