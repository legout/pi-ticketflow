# Fixes: pt-rvpi

## Critical Fix: LogLevel Enum Aliases

### Problem
The LogLevel enum only defined DEBUG, INFO, WARN, ERROR but ralph_new.py referenced VERBOSE, QUIET, and NORMAL, which would cause AttributeError at runtime.

### Solution
Added legacy aliases to the LogLevel enum in `tf_cli/logger.py`:

```python
class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"

    # Legacy aliases for backward compatibility with ralph config
    VERBOSE = "debug"  # Maps to DEBUG for legacy compatibility
    QUIET = "error"    # Maps to ERROR for legacy compatibility
    NORMAL = "info"    # Maps to INFO for legacy compatibility
```

Also updated:
1. `from_string()` to parse "verbose", "quiet", "normal" strings
2. `_should_log()` to use numeric severity comparison instead of list index

### Files Changed
- `tf_cli/logger.py` - Added enum aliases and updated comparison logic

### Verification
```bash
python -c "from tf_cli.logger import LogLevel; print(LogLevel.VERBOSE, LogLevel.QUIET, LogLevel.NORMAL)"
# Output: LogLevel.DEBUG LogLevel.ERROR LogLevel.INFO
```

All 440 tests pass.

## Other Issues Not Fixed

The following issues were identified but not fixed as they are pre-existing or out of scope:

1. **Lock file race condition** - Pre-existing TOCTOU issue in ralph_new.py
2. **Sequential wait in parallel mode** - Existing architectural issue
3. **Non-atomic progress file updates** - Existing issue requiring larger refactor
4. **Missing lifecycle events from pt-l6yb spec** - Out of scope for pt-rvpi

These should be addressed in follow-up tickets.
