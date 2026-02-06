# Ralph Logging

Ralph provides structured, actionable logging to help you understand what the autonomous loop is doing and diagnose issues when they occur.

---

## Quick Start

### Normal Mode (Default)

```bash
tf ralph start
```

Shows lifecycle events: ticket selection, phase transitions, completions, and errors.

### Verbose Mode

```bash
tf ralph start --verbose
# or
RALPH_VERBOSE=1 tf ralph start
```

Adds detailed diagnostics: command execution, timing metrics, subagent activity.

### Quiet Mode

```bash
tf ralph start --quiet
# or
RALPH_QUIET=1 tf ralph start
```

Minimal output: start, end, and errors only. Useful for CI.

---

## Log Format

```
TIMESTAMP [LEVEL] [iteration:N] [ticket:TICKET_ID] [phase:PHASE] message
```

**Example:**
```
2026-02-06T17:45:12Z [INFO] [iteration:3] [ticket:pt-abc123] [phase:implement] Starting implementation
```

---

## Log Levels

| Level | Description | Shown In |
|-------|-------------|----------|
| `ERROR` | Failures that stop or may stop processing | All modes |
| `WARN`  | Recoverable issues, unusual conditions | All modes |
| `INFO`  | Normal lifecycle events | Normal, Verbose |
| `DEBUG` | Detailed diagnostics | Verbose only |

---

## Key Events

### Loop Lifecycle

| Event | Description |
|-------|-------------|
| `loop_start` | Ralph initialized with config |
| `loop_end` | Ralph terminated (complete/max_iter/error) |
| `iteration_start` | Beginning work on a ticket |
| `iteration_end` | Finished work on a ticket |

### Ticket Lifecycle

| Event | Description |
|-------|-------------|
| `ticket_selected` | Ticket chosen for processing |
| `ticket_skipped` | Ticket bypassed (deps, not ready) |
| `phase_transition` | Moving between workflow phases |

### Workflow Phases

- `reanchor` - Loading context
- `research` - Knowledge gathering
- `implement` - Code changes
- `review` - Parallel reviews
- `fix` - Issue resolution
- `close` - Ticket closure

---

## Grepping Logs

```bash
# Find all errors
grep "\[ERROR\]" .tf/ralph/logs/*.log

# Find specific ticket activity
grep "\[ticket:pt-abc123\]" .tf/ralph/logs/*.log

# Find phase transitions
grep "phase:" .tf/ralph/logs/*.log

# Find completed tickets
grep "Ticket completed: COMPLETE" .tf/ralph/logs/*.log

# Find failed tickets
grep "Ticket completed: FAILED" .tf/ralph/logs/*.log
```

---

## Security & Privacy

### Redaction

Sensitive data is automatically redacted:

- **API keys, tokens, passwords** → `[REDACTED]`
- **Environment variables** with `KEY`, `TOKEN`, `SECRET` → `[REDACTED]`
- **Long paths** truncated in normal mode (full in verbose)

### Never Logged

Even in verbose mode:
- Full Pi prompt content
- Complete review outputs
- Internal session data

---

## Log Files

When file logging is enabled (`RALPH_LOG_FILE=1` or set `logFile: true` in `.tf/ralph/config.json`):

- **Path**: `.tf/ralph/logs/YYYY-MM-DD.log`
- **Retention**: 7 days
- **Levels**: All (including DEBUG)

---

## Troubleshooting

### "No ready tickets found"

Check `tk ready` - are there tickets with unmet dependencies?

### Loop stops early

Check `.tf/ralph/progress.md` for failures and last state.

### Too much output

Use `--quiet` mode or filter with grep:
```bash
tf ralph start 2>&1 | grep -E "(ERROR|loop_|Ticket completed)"
```

### Debug a specific ticket

Run single ticket with verbose:
```bash
tf ralph run pt-abc123 --verbose
```

---

## Specification

For the full technical specification, see:
- `../.tf/knowledge/tickets/pt-l6yb/ralph-logging-spec.md` (from this docs directory)

This defines:
- Complete event reference
- Redaction rules
- Phase values
- Error context format
- Implementation notes for developers
