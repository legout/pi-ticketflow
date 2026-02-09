# Fixes: abc-123

## Issues Fixed

### Minor: Remove redundant `name is None` check
- **File**: `demo/hello.py:22`
- **Issue**: The type hint `name: str` means None can never be passed through the public API, making the `name is None` check dead code.
- **Fix**: Changed condition from `if name is None or not name.strip():` to `if not name.strip():`
- **Verification**: All 4 tests still pass after the change.

## Issues Not Fixed (Intentional)
- Warning about long name validation - not required for demo utility
- Suggestions for `__version__` and parametrized tests - nice-to-have for follow-up

## Test Results After Fixes
```
pytest tests/test_demo_hello.py -v
4 passed
```
