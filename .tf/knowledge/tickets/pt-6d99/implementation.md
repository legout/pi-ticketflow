# Implementation: pt-6d99

## Summary
Defined and codified the dispatch-default Ralph execution contract. Added `--dispatch` and `--no-interactive-shell` flags to `tf ralph run` and `tf ralph start` commands, with appropriate configuration options and help text.

This implementation fixes the Critical and Major issues identified in the previous review:
- Added validation for invalid execution_backend values (Critical fix)
- Extracted shared `resolve_execution_backend()` function to eliminate duplicate code
- Fixed misleading log message about subprocess fallback
- Fixed backward compatibility logic for interactiveShell.enabled config

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Files Changed
- `tf/ralph.py` - Added execution backend contract:
  - Added `VALID_EXECUTION_BACKENDS` constant
  - Added `resolve_execution_backend()` shared function (fixes Major duplicate code)
  - Updated `ralph_run()` to use `resolve_execution_backend()` 
  - Updated `ralph_start()` to use `resolve_execution_backend()`
  - Fixed validation to warn on invalid config/CLI values (fixes Critical)
  - Fixed backward compatibility logic for `interactiveShell.enabled`
  - Fixed misleading log message in `run_ticket()`
  - Updated `usage()` help text to document the reserved `interactiveShell.mode` option

- `tf/ralph/__init__.py` - Exported new function and constant:
  - Added `resolve_execution_backend` to exports
  - Added `VALID_EXECUTION_BACKENDS` to exports

## Key Decisions
1. **Default behavior**: `--dispatch` is the default (when no flag specified). This aligns with the ticket acceptance criteria.
2. **Flag precedence**: CLI flag → `RALPH_NO_INTERACTIVE_SHELL` env var → config → default
3. **Backward compatibility**: The `interactiveShell.enabled` config key is checked as a fallback for existing configs (only when `executionBackend` key is NOT present in config)
4. **Contract definition only**: Actual dispatch implementation (via `interactive_shell` tool) is deferred to pt-9yjn. Current implementation logs the intent but uses subprocess for both backends.
5. **Help text**: Updated usage documentation to clearly explain the new flags and their relationship to legacy behavior.
6. **Warning on invalid config**: When users provide an invalid `executionBackend` value, a warning is logged and the default is used, making it easier to debug configuration issues.

## Tests Run
```bash
# Unit tests for resolve_execution_backend - all passed
python -c "from unittest.mock import MagicMock; import tf.ralph as ralph; ..."

# Flag parsing tests - all passed
python -c "import tf.ralph as ralph; ..."

# Syntax check
python -m py_compile tf/ralph.py
# Result: Syntax OK

# Full test suite
pytest tests/test_ralph*.py -v
# Result: 89 tests, 79 passed, 10 failed (failures unrelated to this change - pre-existing lock file and test structure issues)
```

## Verification
1. ✅ `--dispatch` flag parsed correctly for both `run` and `start`
2. ✅ `--no-interactive-shell` flag parsed correctly for both `run` and `start`
3. ✅ Default behavior (no flag) uses dispatch as default
4. ✅ Help text updated with Execution Backend Options section
5. ✅ Config options documented: `executionBackend`, `interactiveShell.enabled`
6. ✅ Environment variable `RALPH_NO_INTERACTIVE_SHELL` documented
7. ✅ Invalid config/CLI values now log warnings and use default (Critical fix)
8. ✅ Shared function eliminates duplicate code (Major fix)
9. ✅ Backward compatibility logic correctly handles `interactiveShell.enabled`
10. ✅ Log message no longer misleading (Major fix)

## Usage Examples
```bash
# Use dispatch mode (default)
tf ralph run pt-1234
tf ralph run pt-1234 --dispatch
tf ralph start --dispatch

# Use legacy subprocess backend
tf ralph run pt-1234 --no-interactive-shell
tf ralph start --no-interactive-shell

# Via environment variable
RALPH_NO_INTERACTIVE_SHELL=1 tf ralph run pt-1234

# Via config (.tf/ralph/config.json)
{
  "executionBackend": "subprocess"
}
```

## Review Fixes Applied

### Critical (must fix) - FIXED
- Invalid config values now log a warning and use default instead of silently falling through

### Major (should fix) - FIXED
- Extracted `resolve_execution_backend()` function to eliminate duplicate logic in `ralph_run()` and `ralph_start()`
- Fixed confusing backward compatibility logic - now only applies when `executionBackend` key is NOT in config
- Fixed misleading log message in `run_ticket()` - now says "pending pt-9yjn implementation" instead of claiming to use dispatch when actually using subprocess

### Minor (nice to fix) - ADDRESSED
- Documented `interactiveShell.mode` as "reserved for future use" in defaults comment
