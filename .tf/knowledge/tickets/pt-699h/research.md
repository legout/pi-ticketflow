# Research: pt-699h

## Status
Research completed

## Rationale
Research was performed to understand:
1. The existing parallel scheduling infrastructure in Ralph
2. How dispatch sessions are launched and monitored
3. Component-tag safety mechanisms already in place
4. Dependencies (pt-7jzy) and dependents (pt-8qk8) for coordination

## Context Reviewed

### Ticket Details (pt-699h)
- **Task**: Implement parallel dispatch scheduling with component safety
- **Goal**: Run multiple dispatch sessions concurrently while honoring dependency and component-tag safety rules
- **Acceptance Criteria**:
  - Parallel scheduler launches up to configured worker count
  - Tickets with conflicting components are not started together
  - Dependent tickets wait for prerequisite completion
- **Constraints**: Keep conservative scheduling behavior (prefer safety over throughput)

### Dependencies

#### pt-7jzy (COMPLETED) - Dispatch Completion Handling
- Implemented `tf/ralph_completion.py` with:
  - `poll_dispatch_status(pid)` - Non-blocking process status check
  - `graceful_terminate_dispatch()` - SIGTERM → SIGKILL sequence
  - `wait_for_dispatch_completion()` - Main monitoring with timeout
  - `DispatchCompletionStatus` enum: RUNNING, COMPLETED, TIMEOUT, TERMINATED, ERROR
  - `DispatchCompletionResult` dataclass with full termination details
- Dispatch tracking files stored at `.tf/ralph/dispatch/{ticket}.json`

#### pt-8qk8 (DEPENDS ON pt-699h) - Orphaned Session Recovery
- Startup scans for orphaned sessions from prior runs
- Kills/cleans orphaned sessions before new scheduling
- Enforces retention TTL for finished session metadata

### Existing Parallel Scheduling Infrastructure

From `tf/ralph.py`:

```python
def extract_components(ticket_id: str, tag_prefix: str, allow_untagged: bool) -> Optional[set]:
    """Extract component tags from ticket (tags starting with 'component:')."""

def select_parallel_tickets(ready: List[str], max_parallel: int, allow_untagged: bool, tag_prefix: str) -> List[str]:
    """Select tickets that don't have conflicting components."""
```

These functions are already used by the worktree-based parallel mode and should be reused for dispatch scheduling.

### Dispatch Session Infrastructure

From `tf/ralph.py`:

```python
@dataclass
class DispatchResult:
    session_id: str
    ticket_id: str
    status: str
    pid: Optional[int] = None
    error: Optional[str] = None

def run_ticket_dispatch(ticket: str, ...) -> DispatchResult:
    """Launch a ticket in dispatch mode using subprocess."""
```

From `tf/ralph_completion.py`:
- `wait_for_dispatch_completion()` - Monitors a dispatch session until completion
- Tracks duration, return codes, termination method
- Supports graceful shutdown with configurable timeouts

### Configuration

From `.tf/config/settings.json`:
```json
{
  "parallelWorkers": 1,
  "parallelWorktreesDir": ".tf/ralph/worktrees",
  "parallelAllowUntagged": false,
  "componentTagPrefix": "component:",
  "parallelKeepWorktrees": false,
  "parallelAutoMerge": true
}
```

### Knowledge Topics

**Seed: seed-add-ralph-loop-background-interactive**
- Vision: Fresh context per ticket via background interactive Pi sessions
- Parallel workers run concurrently with dependency/component safeguards
- State continuity: progress.md and AGENTS.md semantics unchanged

**Plan: plan-ralph-background-interactive-shell** (APPROVED)
- Phase 2: "Add parallel coordination for dispatch sessions"
- Track multiple concurrent session IDs
- Use existing component tags for dependency safety
- Wait for session completions before starting dependent tickets

**Spike: spike-interactive-shell-execution**
- Multiple `interactive_shell` background sessions can run concurrently
- Each ticket gets its own session
- Component tags still used for dependency coordination

## Key Implementation Points

1. **Reuse existing component safety**: `extract_components()` and `select_parallel_tickets()` already handle component-tag collision detection

2. **Track active sessions**: Need to track multiple `DispatchResult` objects concurrently

3. **Completion polling**: Use `wait_for_dispatch_completion()` or `poll_dispatch_status()` to check when sessions complete

4. **Dependency ordering**: The existing `get_ready_and_blocked()` function provides ready/blocked ticket sets

5. **Worker limit**: Respect `parallelWorkers` config (default 1, but can be higher)

## Sources

- Ticket: `.tickets/pt-699h.md`
- Dependency: `.tickets/pt-7jzy.md` (completion handling)
- Dependent: `.tickets/pt-8qk8.md` (orphaned session recovery)
- Code: `tf/ralph.py` (parallel scheduling, dispatch functions)
- Code: `tf/ralph_completion.py` (completion monitoring)
- Knowledge: `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/`
- Knowledge: `.tf/knowledge/topics/plan-ralph-background-interactive-shell/plan.md`
- Knowledge: `.tf/knowledge/topics/spike-interactive-shell-execution/spike.md`
- Config: `.tf/config/settings.json`
