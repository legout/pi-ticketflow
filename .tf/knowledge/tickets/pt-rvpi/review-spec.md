# Review (Spec Audit): pt-rvpi

## Overall Assessment
The Ralph logger helper has been implemented with all core requirements from the ticket: level filtering (debug/info/warn/error), ISO timestamps, context fields (ticket id, iteration, mode), stderr output by default, and comprehensive redaction for secrets. The implementation includes 41 passing tests and integrates with ralph_new.py for lifecycle logging. Minor discrepancies exist with the broader pt-l6yb logging spec regarding log format style and complete lifecycle event coverage.

## Critical (must fix)
- `tf_cli/ralph_new.py:310` - `LogLevel.VERBOSE` is used but does not exist in the LogLevel enum (only DEBUG, INFO, WARN, ERROR defined). This will cause an AttributeError at runtime when RALPH_VERBOSE=1 env var is set. Should use `LogLevel.DEBUG` instead.
- `tf_cli/ralph_new.py:320` - `log_level_to_flag()` references `LogLevel.VERBOSE` and `LogLevel.QUIET` which don't exist in the enum, causing mapping to fail for these levels.

## Major (should fix)
- `tf_cli/logger.py:126-141` - Log format uses pipe-delimited `key=value` style (`2026-02-06T17:54:04Z | INFO | mode=serial | ticket=abc-123 | message`) but the pt-l6yb spec requires bracketed format (`TIMESTAMP [LEVEL] [iteration:N] [ticket:TICKET_ID] [phase:PHASE] message`). The current format is greppable but doesn't match the documented spec format.
- `tf_cli/ralph_new.py` - `loop_start` and `loop_end` events are partially logged (general info messages) but don't follow the specific lifecycle event format from the spec with iteration/ticket context fields consistently applied.

## Minor (nice to fix)
- `tf_cli/logger.py:1` - Module docstring could reference the ticket ID (pt-rvpi) and link to the ralph-logging spec for traceability.
- `tf_cli/logger.py:86-93` - The `RedactionHelper._looks_like_secret()` heuristic could include additional token patterns (e.g., `glpat-` for GitLab, `xoxb-` for Slack) to be more comprehensive.

## Warnings (follow-up ticket)
- `tf_cli/ralph_new.py` - Several lifecycle events from pt-l6yb spec are not implemented: `ticket_selected` (with reason), `ticket_skipped`, `ticket_not_found`, `command_start`, `command_end`, `config_loaded`, `progress_saved`, `lesson_extracted`. These are documented in the spec but not required for pt-rvpi scope.
- `tf_cli/logger.py:13-16` - The spec defines QUIET and VERBOSE as modes, but the LogLevel enum only has DEBUG/INFO/WARN/ERROR. This mode/level distinction may need clarification in a follow-up ticket.

## Suggestions (follow-up ticket)
- Consider adding a `set_phase()` context manager method to RalphLogger to automatically track and log phase transitions as specified in pt-l6yb section 9.1.
- Consider supporting file output (`.tf/ralph/logs/YYYY-MM-DD.log`) as specified in pt-l6yb section 6.2 for persistent logging.
- Consider adding structured JSON output option for log aggregation as mentioned in pt-l6yb section 6.3 (future enhancement).

## Positive Notes
- All 41 tests pass with good coverage of LogLevel parsing, redaction behavior, context propagation, and lifecycle methods.
- The redaction implementation is thorough: detects API keys, tokens, secrets, passwords; truncates long values (>1000 chars); handles nested dicts and lists recursively.
- The `with_context()` pattern correctly creates new logger instances to avoid shared state issues in parallel mode.
- The logger defaults to stderr as required, keeping stdout clean for workflow output.
- The integration in ralph_new.py replaces print statements consistently with structured logging calls.
- ISO timestamp format (UTC) matches spec requirements exactly.

## Summary Statistics
- Critical: 2
- Major: 2
- Minor: 2
- Warnings: 2
- Suggestions: 3

## Spec Coverage
- Spec/plan sources consulted:
  - Ticket pt-rvpi acceptance criteria (all 4 criteria implemented)
  - pt-l6yb ralph-logging-spec.md (comprehensive logging spec - partial alignment)
  - docs/ralph-logging.md (user-facing documentation - aligned)
- Missing specs: None (ticket spec fully available)
