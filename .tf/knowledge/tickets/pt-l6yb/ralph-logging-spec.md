# Ralph Logging Specification

**Version**: 1.0  
**Ticket**: pt-l6yb  
**Date**: 2026-02-06

---

## 1. Overview

This document defines the logging behavior for the Ralph autonomous ticket processing loop. The goal is to provide actionable observability without overwhelming users or leaking sensitive information.

---

## 2. Log Format

### 2.1 Line Format

```
TIMESTAMP [LEVEL] [iteration:N] [ticket:TICKET_ID] [phase:PHASE] message
```

### 2.2 Field Definitions

| Field | Format | Example |
|-------|--------|---------|
| `TIMESTAMP` | ISO 8601 UTC | `2026-02-06T17:45:12Z` |
| `LEVEL` | One of: ERROR, WARN, INFO, DEBUG | `[INFO]` |
| `iteration` | Loop iteration number | `[iteration:3]` |
| `ticket` | Ticket ID or `(none)` | `[ticket:pt-abc123]` |
| `phase` | Current workflow phase | `[phase:implement]` |
| `message` | Human-readable description | `Starting implementation` |

**Multi-line Messages**: Log messages must be single-line. Newlines in source data should be:
- Replaced with ` ␊ ` (visible space + newline indicator + space)
- Or truncated at first newline with `[truncated]`
- Stack traces: log first line + `[see artifact:PATH]`

### 2.3 Examples

```
2026-02-06T17:45:10Z [INFO] [iteration:0] [ticket:(none)] [phase:(none)] Ralph loop starting (max_iterations: 50)
2026-02-06T17:45:11Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:(none)] Ticket selected: pt-abc123 (ready, no deps)
2026-02-06T17:45:12Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:reanchor] Phase transition: (none) -> reanchor
2026-02-06T17:45:13Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:implement] Phase transition: reanchor -> implement
2026-02-06T17:46:45Z [ERROR] [iteration:1] [ticket:pt-abc123] [phase:implement] Error: subprocess failed (exit 1). See artifact: .tf/knowledge/tickets/pt-abc123/
2026-02-06T17:46:46Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:(none)] Ticket completed: FAILED (duration: 94.2s)
2026-02-06T17:46:51Z [INFO] [iteration:2] [ticket:(none)] [phase:(none)] No ready tickets found. Waiting 10s...
```

---

## 3. Lifecycle Events

### 3.1 Event Reference

| Event | Level | Always Logged | Description |
|-------|-------|---------------|-------------|
| `loop_start` | INFO | Yes | Ralph loop initialized with config |
| `loop_end` | INFO | Yes | Ralph loop terminated (reason: complete/max_iter/error) |
| `iteration_start` | INFO | Yes | Beginning work on a ticket |
| `iteration_end` | INFO | Yes | Finished work on a ticket (status + duration) |
| `ticket_selected` | INFO | Yes | Ticket chosen for processing (with reason) |
| `ticket_skipped` | WARN | Yes | Ticket bypassed (reason: deps blocked, not ready, etc.) |
| `ticket_not_found` | WARN | Yes | Ticket ID from query returned no data |
| `phase_transition` | INFO | Yes | Moving between workflow phases |
| `command_start` | DEBUG | No | External command invoked (with redacted args) |
| `command_end` | DEBUG | No | Command completed (exit code, duration) |
| `command_retry` | WARN | Yes | Retrying failed command (attempt N of M) |
| `tool_execution` | DEBUG | No | Pi tool called (name only, not args) |
| `research_fetch` | DEBUG | No | Research agent spawned |
| `subagent_spawn` | DEBUG | No | Reviewer/fix subagent started |
| `subagent_complete` | DEBUG | No | Subagent finished (with exit status) |
| `error` | ERROR | Yes | Failure with context (ticket, phase, error type) |
| `warning` | WARN | Yes | Recoverable issue |
| `config_loaded` | DEBUG | No | Config values (sanitized) |
| `progress_saved` | DEBUG | No | Progress.md updated |
| `lesson_extracted` | DEBUG | No | Lesson appended to AGENTS.md |

### 3.2 Phase Values

Valid values for the `phase` field:

| Phase | Description |
|-------|-------------|
| `(none)` | Outside workflow (selection, initialization) |
| `reanchor` | Loading context (AGENTS.md, ticket, knowledge) |
| `research` | Knowledge gathering step |
| `implement` | Code implementation |
| `review` | Parallel review execution |
| `merge` | Review consolidation |
| `fix` | Issue resolution |
| `followups` | Follow-up ticket creation |
| `close` | Ticket closure and commit |

---

## 4. Redaction Rules

### 4.1 Always Redacted

These patterns are **always** replaced with `[REDACTED]` regardless of verbosity level:

| Pattern | Redaction | Example |
|---------|-----------|---------|
| API keys in args | Full value | `--api-key=abc123` → `--api-key=[REDACTED]` |
| Token values | Full value | `Authorization: Bearer tok123` → `Authorization: [REDACTED]` |
| Environment variables | Variable name only | `API_KEY=secret` → `API_KEY=[REDACTED]` |
| Password patterns | Full value | `password=secret123` → `password=[REDACTED]` |
| URL credentials | Full credential portion | `https://user:pass@host` → `https://[REDACTED]@host` |
| SSH private keys | Full key block | `-----BEGIN OPENSSH PRIVATE KEY-----`... → `[REDACTED]` |

**Sensitive environment variable patterns** (case-insensitive):
- `*KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*CREDENTIAL*`, `*AUTH*`, `*PRIVATE_KEY*`, `*SSH_KEY*`

### 4.2 Truncated in INFO, Full in DEBUG

| Data | INFO Mode | DEBUG Mode |
|------|-----------|------------|
| Long file paths | `.../last/40/chars` | Full path |
| Command arguments | First 3 args + `... (+N more)` | All args (redacted) |
| Stdout/Stderr | First 200 chars + `[truncated]` | Full output (redacted) |
| Large JSON payloads | Keys only + `[truncated]` | Full payload (redacted) |
| Ticket descriptions | `(see ticket:TICKET_ID)` | First 500 chars |

### 4.3 Never Logged

Even in DEBUG mode, these are **never** included:

- Full Pi prompt content (reference artifact path instead)
- Internal Pi session state
- Complete review outputs (reference `review.md` path)
- File contents over 10KB (reference path)
- Stack traces from external tools (log exit code + message)

---

## 5. Verbosity Modes

### 5.1 Mode Definitions

| Mode | Flag / Env Var | Events Shown | Use Case |
|------|----------------|--------------|----------|
| `quiet` | `--quiet` or `RALPH_QUIET=1` | loop_start, loop_end, errors | CI/piping |
| `normal` | (default) | All INFO events | Daily use |
| `verbose` | `--verbose` or `RALPH_VERBOSE=1` | INFO + DEBUG | Debugging |

### 5.2 Mode Behavior

**Quiet Mode**:
```
2026-02-06T17:45:10Z [INFO] Ralph loop starting
2026-02-06T17:50:23Z [INFO] Ralph loop complete (5 tickets, 0 failed)
```

**Normal Mode**:
- All lifecycle events (iteration start/end, phase transitions)
- Selection decisions
- Errors and warnings
- Configuration summary at start

**Verbose Mode**:
- All normal output plus:
  - Command execution details
  - Tool invocations
  - Timing metrics per phase
  - Config values (sanitized)
  - Progress save confirmations

---

## 6. Output Destinations

### 6.1 Console Output

- **stdout**: INFO and DEBUG logs (when enabled)
- **stderr**: ERROR and WARN logs (always)

### 6.2 Log File (Optional)

When `RALPH_LOG_FILE=1` or config `logFile: true`:

- **Path**: `.tf/ralph/logs/YYYY-MM-DD.log`
- **Format**: Same as console
- **Rotation**: 7 days retention, auto-cleanup
- **Levels**: All levels (DEBUG even if console is normal)

### 6.3 Structured JSON (Future)

Future enhancement (not in MVP):
- `RALPH_LOG_FORMAT=json`
- Machine-parseable for log aggregation

---

## 7. Error Context

### 7.1 Error Event Format

Single-line format (consistent with all other log lines):

```
2026-02-06T17:46:45Z [ERROR] [iteration:1] [ticket:pt-abc123] [phase:implement] Error: subprocess_failure (exit_code: 1, artifact: .tf/knowledge/tickets/pt-abc123/)
```

For complex errors, log the primary error line followed by additional context lines with `|>` prefix:

```
2026-02-06T17:46:45Z [ERROR] [iteration:1] [ticket:pt-abc123] [phase:implement] Error: subprocess_failure (exit_code: 1)
2026-02-06T17:46:45Z [ERROR] [iteration:1] [ticket:pt-abc123] [phase:implement] |> artifact_path: .tf/knowledge/tickets/pt-abc123/
2026-02-06T17:46:45Z [ERROR] [iteration:1] [ticket:pt-abc123] [phase:implement] |> command: pi -p "/tf pt-abc123 --auto"
2026-02-06T17:46:45Z [ERROR] [iteration:1] [ticket:pt-abc123] [phase:implement] |> retryable: false
```

### 7.2 Context Fields

All error events include:
- `ticket`: Ticket ID being processed
- `phase`: Current workflow phase
- `error_type`: Categorized error (subprocess_failure, config_error, network_error, etc.)
- `artifact_path`: Where to find detailed logs
- `retryable`: Whether automatic retry is appropriate

---

## 8. Greppable Patterns

Users can grep logs for specific information:

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

## 9. Implementation Notes

### 9.1 For Implementers (pt-rvpi, pt-ljos)

1. Create a `RalphLogger` class with methods per level
2. Use context managers for phase tracking (`with logger.phase("implement")`)
3. Implement redaction as a filter layer (prevents accidental leakage)
4. Support both sync and async logging (for parallel mode)

### 9.2 Testing

- Test redaction with known secret patterns
- Verify no secrets in DEBUG output
- Check truncation behavior at boundaries
- Validate JSON doesn't break with special chars

---

## 10. Related Tickets

| Ticket | Description |
|--------|-------------|
| pt-7cri | Configure Ralph verbosity controls (CLI flags + env var) |
| pt-rvpi | Implement Ralph logger helper |
| pt-ljos | Implement lifecycle logging for serial Ralph loop |
| pt-2sea | Implement lifecycle logging for parallel Ralph mode |
| pt-j2it | Document Ralph logging + troubleshooting |

---

## Appendix: Sample Log Output

### Normal Mode (Full Session)

```
2026-02-06T09:00:00Z [INFO] [iteration:0] [ticket:(none)] Ralph loop starting (max_iterations: 50, parallel: 1)
2026-02-06T09:00:00Z [INFO] [iteration:1] [ticket:pt-abc123] Ticket selected: pt-abc123 (ready, no blocking deps)
2026-02-06T09:00:01Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:reanchor] Phase transition: (none) -> reanchor
2026-02-06T09:00:02Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:research] Phase transition: reanchor -> research
2026-02-06T09:00:05Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:implement] Phase transition: research -> implement
2026-02-06T09:02:15Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:review] Phase transition: implement -> review
2026-02-06T09:03:45Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:fix] Phase transition: review -> fix
2026-02-06T09:04:12Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:close] Phase transition: fix -> close
2026-02-06T09:04:15Z [INFO] [iteration:1] [ticket:pt-abc123] Ticket completed: COMPLETE (duration: 254.3s)
2026-02-06T09:04:20Z [INFO] [iteration:2] [ticket:(none)] No ready tickets found. Waiting 5s...
...
2026-02-06T17:30:00Z [INFO] [iteration:0] [ticket:(none)] Ralph loop complete (reason: max_iterations). Processed 50 tickets (48 complete, 2 failed)
<promise>COMPLETE</promise>
```

### Verbose Mode (Snippet)

```
2026-02-06T09:00:05Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:implement] Command: pi -p "/tf pt-abc123 --auto"
2026-02-06T09:00:05Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:implement] Subagent spawned: implementer
2026-02-06T09:02:15Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:implement] Command completed: exit=0, duration=130.2s
2026-02-06T09:02:15Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:implement] Files changed: 3 (see .tf/knowledge/tickets/pt-abc123/files_changed.txt)
2026-02-06T09:02:15Z [INFO] [iteration:1] [ticket:pt-abc123] [phase:review] Phase transition: implement -> review
2026-02-06T09:02:16Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:review] Subagent spawned: reviewer-general (model: gpt-5.1-codex-mini)
2026-02-06T09:02:16Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:review] Subagent spawned: reviewer-spec-audit (model: gpt-5.2-codex)
2026-02-06T09:02:16Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:review] Subagent spawned: reviewer-second-opinion (model: grok-code-fast-1)
2026-02-06T09:03:30Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:review] Subagent complete: reviewer-general (exit=0)
2026-02-06T09:03:35Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:review] Subagent complete: reviewer-spec-audit (exit=0)
2026-02-06T09:03:45Z [DEBUG] [iteration:1] [ticket:pt-abc123] [phase:review] Subagent complete: reviewer-second-opinion (exit=0)
```
