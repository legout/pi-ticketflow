# Implementation: pt-l6yb

## Summary
Defined the Ralph logging specification covering log format, lifecycle events, and redaction rules. The spec ensures consistent, readable logs that aid debugging without leaking secrets or overwhelming users.

## Files Changed
- `.tf/knowledge/tickets/pt-l6yb/ralph-logging-spec.md` - The logging specification document
- `docs/ralph-logging.md` - User-facing documentation referencing the spec

## Key Decisions

### 1. Log Format: Structured but Human-Readable
- **Format**: `TIMESTAMP [LEVEL] [iteration:N] [ticket:TICKET_ID] [phase:PHASE] message`
- **Example**: `2026-02-06T17:45:12Z [INFO] [iteration:3] [ticket:pt-abc123] [phase:implement] Starting implementation`
- **Rationale**: Structured enough for grepping (`grep "phase:implement"`), human-readable for terminal output

### 2. Log Levels
- `ERROR` - Failures that stop or may stop ticket processing
- `WARN`  - Recoverable issues, unusual conditions
- `INFO`  - Normal lifecycle events (default verbosity)
- `DEBUG` - Detailed diagnostics (verbose mode only)

### 3. Lifecycle Events Enumerated (18 events)

| Event | Level | Fields | Description |
|-------|-------|--------|-------------|
| `loop_start` | INFO | max_iterations | Ralph loop initialized |
| `loop_end` | INFO | iterations, completed, failed | Ralph loop completed |
| `iteration_start` | INFO | iteration, ticket_id | Beginning ticket processing |
| `iteration_end` | INFO | iteration, ticket_id, status, duration_ms | Ticket completed/failed |
| `ticket_selected` | INFO | ticket_id, reason | Why this ticket was chosen |
| `ticket_skipped` | WARN | ticket_id, reason | Why ticket was skipped (deps, etc.) |
| `ticket_not_found` | WARN | ticket_id | Ticket ID from query returned no data |
| `phase_transition` | INFO | from, to, ticket_id | Moving between workflow phases |
| `command_start` | DEBUG | command, ticket_id | External command invoked |
| `command_end` | DEBUG | command, exit_code, duration_ms | Command completed |
| `command_retry` | WARN | command, attempt, max_attempts | Retrying failed command |
| `tool_execution` | DEBUG | tool_name, ticket_id | Pi tool called (name only) |
| `research_fetch` | DEBUG | query_count | Research agent spawned |
| `subagent_spawn` | DEBUG | agent_name, model | Reviewer/fix subagent started |
| `subagent_complete` | DEBUG | agent_name, exit_status | Subagent finished |
| `config_loaded` | DEBUG | keys | Config values (sanitized) |
| `progress_saved` | DEBUG | path | Progress.md updated |
| `lesson_extracted` | DEBUG | ticket_id | Lesson appended to AGENTS.md |
| `error` | ERROR | ticket_id, phase, error_type, context | Failure with context |

### 4. Phase Values (9 phases)
- `(none)` - Outside workflow (selection, initialization)
- `reanchor` - Context loading
- `research` - Knowledge gathering
- `implement` - Code changes
- `review` - Parallel reviews
- `merge` - Review consolidation
- `fix` - Issue resolution
- `followups` - Follow-up ticket creation
- `close` - Ticket closure

### 5. Redaction Rules

**Always Redacted (replace with `[REDACTED]`)**:
- API keys, tokens, passwords in command arguments
- Environment variables containing `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `API_KEY`
- Full tool output when it contains credential patterns

**Truncated in INFO, Full in DEBUG**:
- File paths over 80 chars (show `.../last/30/chars`)
- Command arguments lists over 5 args (show count)
- Large stdout/stderr (first/last 200 chars with `[...truncated...]`)

**Never Logged**:
- Full prompt content (even in DEBUG - use artifact paths instead)
- Full ticket descriptions (reference ticket_id instead)
- Internal Pi session data

### 6. Verbosity Modes

**Normal Mode (default)**:
- Shows: loop_start/end, iteration_start/end, ticket_selected/skipped, phase_transition, error
- Hides: command_start/end, debug details

**Verbose Mode (`--verbose` or `RALPH_VERBOSE=1`)**:
- Shows all INFO + DEBUG events
- Includes command execution details
- Includes timing metrics

**Quiet Mode (`--quiet` or `RALPH_QUIET=1`)**:
- Shows only: loop_start, loop_end, errors
- For CI/piping scenarios

### 7. Output Destinations
- **stdout**: Normal/verbose logs (human-readable)
- **stderr**: Errors and warnings (always, even in quiet mode)
- **File**: Optional `.tf/ralph/logs/YYYY-MM-DD.log` with all levels (rotation: 7 days)

## Tests Run
- N/A (specification task - no code changes)

## Verification
1. Review spec: `cat .tf/knowledge/tickets/pt-l6yb/ralph-logging-spec.md`
2. Check it satisfies all acceptance criteria from ticket `pt-l6yb`

## Unblocks
- pt-7cri (Configure Ralph verbosity controls)
- pt-rvpi (Implement Ralph logger helper)
