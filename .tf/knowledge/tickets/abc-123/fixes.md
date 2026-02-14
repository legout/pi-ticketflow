# Fixes: abc-123

## Summary
Fixed 4 Major issues identified in code review. All fixes applied successfully with 14 tests passing.

## Fixes by Severity

### Critical (must fix)
- [ ] None

### Major (should fix)
- [x] `demo/hello.py:50` - **Unicode zero-width character handling bug**: Fixed by separating the regex into two steps - first remove zero-width chars (U+200B-U+200D, U+FEFF), then collapse whitespace. This prevents inserting spaces where zero-width chars were removed from inside words (e.g., "Ali\u200Bce" now correctly becomes "Alice" not "Ali ce").

- [x] `demo/hello.py:35` - **Regex compiled on each call**: Fixed by moving regex compilation to module level with `_ZERO_WIDTH_RE` and `_WHITESPACE_RE` constants. This eliminates O(n) overhead per call.

- [x] `demo/hello.py:33` - **Error message inconsistency**: Fixed by special-casing None in error messages. Now shows "got None" instead of "got NoneType" for better readability.

- [x] `demo/__main__.py:38` - **No BrokenPipeError handling**: Fixed by wrapping `print()` in try/except to catch BrokenPipeError and exit silently with code 0 when output is piped and reader closes early.

### Minor (nice to fix)
- [x] `tests/test_demo_hello.py:59` - Added `test_hello_zero_width_inside_word()` test to verify zero-width chars inside words are removed without adding spaces. This prevents regression of the Major bug.

- [x] `demo/hello.py:27-30` - Updated docstring to accurately reflect behavior: "If the result is empty after cleaning, 'Hello, World!' is returned" instead of just "Empty strings and whitespace-only strings".

### Warnings (follow-up)
- [ ] None fixed (deferred to follow-up tickets)

### Suggestions (follow-up)
- [ ] None fixed (deferred to follow-up tickets)

## Summary Statistics
- **Critical**: 0 fixed
- **Major**: 4 fixed
- **Minor**: 2 fixed
- **Warnings**: 0 fixed
- **Suggestions**: 0 fixed

## Files Changed
- `demo/hello.py` - Fixed Unicode handling, module-level regex compilation, improved error messages, updated docstring
- `demo/__main__.py` - Added BrokenPipeError handling
- `tests/test_demo_hello.py` - Added test for zero-width chars inside words, updated test for None error message

## Verification
- All 14 tests passing (added 1 new test)
- Python syntax validation: ✅ Passed
- Test commands run:
  ```bash
  python -m pytest tests/test_demo_hello.py -v
  # 14 passed in 0.05s
  ```
