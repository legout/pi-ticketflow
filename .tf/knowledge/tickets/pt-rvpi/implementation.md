# Implementation: pt-rvpi

## Summary
Implemented a structured logging helper for Ralph with level filtering, timestamps, context fields, stderr output, and redaction capabilities.

## Files Changed

### New Files
- `tf_cli/logger.py` - New logging module with:
  - `LogLevel` enum (DEBUG, INFO, WARN, ERROR)
  - `RalphLogger` class with context support and convenience methods
  - `RedactionHelper` class for sensitive data detection and truncation
  - `create_logger()` factory function
  - All logs go to stderr by default
  - ISO timestamp format (UTC)
  - Context fields: ticket id, iteration, mode (serial/parallel)

- `tests/test_logger.py` - Comprehensive test suite (41 tests):
  - LogLevel parsing tests
  - Redaction helper tests (sensitive key detection, truncation, secret detection)
  - Logger output format tests
  - Context propagation tests
  - Lifecycle logging method tests

### Modified Files
- `tf_cli/ralph_new.py` - Integrated new logger:
  - Replaced inline LogLevel enum with import from logger module
  - Updated `ensure_ralph_dir()` to accept optional logger
  - Updated `prompt_exists()` to accept optional logger
  - Updated `sanitize_ticket_query()` to accept optional logger
  - Updated `lock_acquire()` to accept optional logger
  - Updated `run_ticket()` to use logger for all output
  - Refactored `ralph_run()` to create and use logger with ticket context
  - Refactored `ralph_start()` to create and use logger with mode/ticket/iteration context
  - Replaced print statements with structured logging calls
  - Added lifecycle logging: `log_ticket_start()`, `log_ticket_complete()`, `log_error_summary()`

## Key Decisions

1. **Kept usage() on stdout**: Help text remains on stdout as it's primary output, not diagnostic logging
2. **Kept promise sigil on stdout**: `<promise>COMPLETE</promise>` is a protocol message, not a log
3. **Context propagation via with_context()**: Creates new logger instances to avoid shared state issues in parallel mode
4. **Redaction before formatting**: Sensitive data is redacted at the dict level before string formatting
5. **Quoted values with spaces**: Values containing spaces are wrapped in quotes for clean parsing
6. **Backward compatibility**: All logger parameters are optional; functions work without logger for gradual migration

## Test Coverage
- 41 new tests added for logger module
- All 440 tests pass (399 existing + 41 new)
- Manual verification: ran `python -c "from tf_cli.logger import *; print('Import OK')"`

## Verification Commands
```bash
# Run all tests
source .venv/bin/activate && python -m pytest tests/ -v

# Verify imports work
python -c "from tf_cli.logger import RalphLogger, create_logger; print('OK')"
python -c "from tf_cli.ralph_new import ralph_run; print('OK')"

# Syntax check
python -m py_compile tf_cli/logger.py tf_cli/ralph_new.py
```

## Log Output Format
```
2026-02-06T17:54:04Z | INFO | mode=serial | ticket=abc-123 | Starting ticket processing: abc-123
2026-02-06T17:54:04Z | ERROR | error="Command failed" | mode=serial | ticket=abc-123 | Error summary
```

## Redaction Examples
- API keys, tokens, secrets: `[REDACTED]`
- Long values (>1000 chars): truncated with `[TRUNCATED]` suffix
- Sensitive key names trigger redaction of entire value
