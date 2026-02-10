# Fixes: pt-lbvu

## Summary
Fixed 1 Major issue identified in code review related to error handling in `load_escalation_config()`.

## Changes Made

### tf/retry_state.py
**Issue**: `load_escalation_config()` silently swallowed all `IOError` exceptions including permission errors, potentially masking configuration issues.

**Fix**: Distinguished `PermissionError` from other `IOError` exceptions:
- `PermissionError` is now logged as ERROR level (more prominent)
- Other `IOError` exceptions remain as WARNING level
- Both cases still return default config for graceful degradation

**Diff**:
```python
# Before:
except IOError as e:
    # File exists but can't be read (permissions, etc.) - log warning and return defaults
    logger.warning(f"Cannot read settings file {path}: {e}. Using default escalation config.")
    return dict(DEFAULT_ESCALATION_CONFIG)

# After:
except PermissionError as e:
    # Permission denied - this is a configuration issue user should know about
    logger.error(f"Permission denied reading settings file {path}: {e}. Check file permissions.")
    return dict(DEFAULT_ESCALATION_CONFIG)
except IOError as e:
    # Other IO errors (locked file, etc.) - log warning and return defaults
    logger.warning(f"Cannot read settings file {path}: {e}. Using default escalation config.")
    return dict(DEFAULT_ESCALATION_CONFIG)
```

## Test Results
All 60 tests in `tests/test_retry_state.py` pass after the fix.

## Verification
- [x] Major issue fixed
- [x] Tests pass
- [x] No breaking changes (still returns defaults for all error cases)
