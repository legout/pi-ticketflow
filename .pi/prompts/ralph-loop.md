---
description: Autonomous ticket processing using dispatch sessions (native interactive_shell)
model: minimax/MiniMax-M2.5
thinking: high
---

# /ralph-loop

Autonomous ticket processing loop using native `interactive_shell` dispatch mode.

Each ticket runs in a fresh, isolated Pi session. Multiple tickets can execute
in parallel. Completion is detected via triggerTurn notifications.

## Usage

```
/ralph-loop [options]

Options (via $ARGUMENTS):
  --max N           Max iterations (default: 50)
  --parallel N      Max concurrent sessions (default: 1)
  --no-worktree     Skip worktree isolation (run in main repo)
  --dry-run         Log what would happen without executing
  --help            Show this help
```

## Architecture

```
This Pi Session (orchestrator)
    │
    ├── interactive_shell(dispatch, background) → pi /tf ticket-1
    │       └── Fresh isolated context
    │       └── triggerTurn notification on completion
    │
    ├── interactive_shell(dispatch, background) → pi /tf ticket-2
    │       └── Fresh isolated context
    │       └── triggerTurn notification on completion
    │
    └── ... (parallel sessions up to --parallel limit)
```

**Key difference from Python Ralph**: This uses the `interactive_shell` tool
directly with dispatch mode, providing true background execution and
triggerTurn notifications. No subprocess polling needed.

## State Files

Same as Python Ralph:
- `.tf/ralph/config.json` - Configuration
- `.tf/ralph/progress.md` - Loop state and history
- `.tf/ralph/AGENTS.md` - Lessons learned
- `.tf/ralph/dispatch-sessions.json` - Active session tracking

---

## Initialization

Before starting the loop, ensure state is initialized:

```bash
# Check .tf/ralph exists
if [ ! -d .tf/ralph ]; then
  echo "Error: Ralph not initialized. Run: tf ralph init"
  exit 1
fi
```

---

## Main Loop

### Loop State (track in context)

```
iteration: 0
max_iterations: <from --max or config>
parallel_limit: <from --parallel or config>
active_sessions: {}  # {session_id: {ticket, start_time, worktree_path}}
completed: []
failed: []
use_worktree: true  # unless --no-worktree
```

### Loop Procedure

```
WHILE iteration < max_iterations:

  # 1. PROCESS COMPLETED SESSIONS
  # Check for any triggerTurn notifications that arrived
  # Update completed/failed lists
  # Clean up worktrees for completed sessions

  # 2. CHECK BACKLOG
  IF backlog_empty():
    IF no active sessions:
      EMIT <promise>COMPLETE</promise>
      STOP
    ELSE:
      WAIT for active sessions to complete
      CONTINUE

  # 3. GET READY TICKETS
  tickets = get_ready_tickets(parallel_limit - len(active_sessions))

  # 4. RESPECT COMPONENT CONSTRAINTS
  tickets = filter_by_component_safety(tickets, active_sessions)

  # 5. LAUNCH DISPATCH SESSIONS
  FOR each ticket IN tickets:
    worktree_path = None
    IF use_worktree:
      worktree_path = create_worktree(ticket)

    session_id = launch_dispatch(ticket, worktree_path)
    active_sessions[session_id] = {
      ticket: ticket,
      start_time: now(),
      worktree_path: worktree_path
    }

    iteration += 1

  # 6. WAIT OR CONTINUE
  IF parallel_limit == 1:
    WAIT for session completion (triggerTurn)
  ELSE:
    CONTINUE (dispatch sessions run in background)

END WHILE

# Max iterations reached
EMIT <promise>COMPLETE</promise>
```

---

## Helper Functions

### backlog_empty()

```bash
tk ready | grep -q .
# Exit code 0 = tickets available, 1 = empty
```

### get_ready_tickets(limit)

```bash
tk ready | head -{limit} | awk '{print $1}'
```

### filter_by_component_safety(tickets, active_sessions)

Get component tags for each ticket. Exclude tickets whose component
tags overlap with currently running sessions.

```bash
# Get component tags for a ticket
tk show {ticket} | grep -E "^tags:" | grep -oE "component:[^,]+"
```

### create_worktree(ticket)

```bash
# Create isolated worktree for ticket
worktree_path=".tf/ralph/worktrees/{ticket}"
git worktree add -b ralph/{ticket} {worktree_path} main 2>/dev/null || \
git worktree add {worktree_path} main
echo $worktree_path
```

### launch_dispatch(ticket, worktree_path)

```
USE interactive_shell:
  command: 'pi /tf {ticket} --auto'
  mode: 'dispatch'
  background: true
  cwd: worktree_path (if set) or current directory

RETURNS: session_id
```

The session runs in background. You will receive a triggerTurn notification
when it completes.

---

## Handling triggerTurn Notifications

When a dispatch session completes, you receive a triggerTurn with the session
output. Handle it like this:

```
ON triggerTurn(session_id, output):

  1. LOOK UP session in active_sessions
  2. PARSE result:
     - Check for <promise>TICKET_{id}_COMPLETE</promise> → success
     - Check for error patterns → failure
     - Check exit code if available

  3. UPDATE state:
     - Remove from active_sessions
     - Add to completed[] or failed[]

  4. HANDLE WORKTREE:
     IF success:
       merge_and_close_worktree(session.worktree_path, session.ticket)
     ELSE:
       cleanup_worktree(session.worktree_path, session.ticket)

  5. UPDATE PROGRESS FILE:
     append_to_progress(session.ticket, status)

  6. EXTRACT LESSONS (optional):
     IF significant learning:
       append_to_agents_md(lesson)

  4. CONTINUE loop (check for more tickets)
```

---

## Worktree Lifecycle

### merge_and_close_worktree(worktree_path, ticket)

```bash
# Merge changes back to main
git -C {worktree_path} add -A
git -C {worktree_path} commit -m "Ralph: complete {ticket}" || true
git checkout main
git merge --no-ff ralph/{ticket} -m "Merge ralph/{ticket}"
git worktree remove {worktree_path}
git branch -d ralph/{ticket}
```

### cleanup_worktree(worktree_path, ticket)

```bash
# Safe cleanup without merge
git worktree remove --force {worktree_path} 2>/dev/null || \
  rm -rf {worktree_path}
git branch -D ralph/{ticket} 2>/dev/null || true
```

---

## Progress File Updates

### append_to_progress(ticket, status)

Append to `.tf/ralph/progress.md`:

```markdown
### {ticket}: {STATUS}
- Started: {start_time}
- Completed: {end_time}
- Duration: {duration}
- Session: {session_id}
- Summary: {one-line from ticket or result}

---
```

Update statistics section:
```markdown
## Statistics
- Iterations: {iteration}
- Completed: {len(completed)}
- Failed: {len(failed)}
- Last updated: {timestamp}
```

---

## Lessons Extraction

After significant tickets, extract lessons to `.tf/ralph/AGENTS.md`:

```markdown
## Lesson from {ticket} ({date})

**Context**: {brief context of what was being done}

**Lesson**: {what was learned}

**Apply when**: {conditions where this applies}

---
```

Only extract when:
- A non-obvious gotcha was discovered
- A repeatable pattern emerged
- Technical debt or architectural insight found
- Tool/environment quirk encountered

---

## Completion

When the loop terminates (backlog empty or max iterations):

1. Wait for any remaining active sessions
2. Write final summary to `.tf/ralph/progress.md`:

```markdown
## Loop Complete

- Status: COMPLETE
- Ended: {timestamp}
- Total iterations: {iteration}
- Completed: {len(completed)}
- Failed: {len(failed)}
- Tickets: {list of completed and failed}

---
```

3. Emit promise sigil:
```
<promise>COMPLETE</promise>
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| No tickets ready | If no active sessions: complete. Else: wait |
| Dispatch launch fails | Log error, mark failed, continue |
| Worktree creation fails | Log error, mark failed, continue |
| Session timeout | Kill session, mark failed, cleanup worktree |
| Merge conflict | Log error, mark failed, preserve worktree for manual review |

---

## Configuration

Read from `.tf/ralph/config.json`:

```json
{
  "maxIterations": 50,
  "parallelWorkers": 1,
  "useWorktrees": true,
  "ticketQuery": "tk ready | head -1 | awk '{print $1}'",
  "completionCheck": "tk ready | grep -q .",
  "workflow": "/tf",
  "workflowFlags": "--auto",
  "sleepBetweenTickets": 5000,
  "promiseOnComplete": true
}
```

CLI arguments override config file.

---

## Comparison to Python Ralph

| Feature | Python Ralph | /ralph-loop |
|---------|--------------|-------------|
| Execution | subprocess.Popen | interactive_shell dispatch |
| Completion detection | Polling waitpid | triggerTurn notification |
| Fresh context | New process | New Pi session |
| Parallel support | Worktrees + subprocess | Multiple dispatch sessions |
| Timeout handling | Built-in | Must implement manually |
| Orphan recovery | On startup | Not in this version |
| State tracking | Python + files | Files only |

---

## Example Session

```
User: /ralph-loop --parallel 2 --max 10

Agent: Starting Ralph loop with parallel=2, max=10

[Iteration 1]
Checking backlog... 3 tickets ready
Launching dispatch for pt-123... session=rapture-owl
Launching dispatch for pt-456... session=calm-reef
Active sessions: 2

[triggerTurn: rapture-owl completed]
pt-123: COMPLETE (exit 0)
Merging worktree... done
Progress updated.

[Iteration 2]
Checking backlog... 2 tickets ready
Launching dispatch for pt-789... session=bold-wave
Active sessions: 2 (calm-reef, bold-wave)

[triggerTurn: calm-reef completed]
pt-456: FAILED (exit 1)
Cleaning up worktree... done
Progress updated.

[triggerTurn: bold-wave completed]
pt-789: COMPLETE (exit 0)
Merging worktree... done

[Iteration 3]
Checking backlog... empty
No active sessions.

## Loop Complete
- Iterations: 3
- Completed: 2 (pt-123, pt-789)
- Failed: 1 (pt-456)

<promise>COMPLETE</promise>
```
