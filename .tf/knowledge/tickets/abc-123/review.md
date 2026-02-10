# Review: abc-123

Merged review from reviewer-general, reviewer-spec-audit, reviewer-second-opinion

## Critical (must fix)
No issues found.

## Major (should fix)

### demo/hello.py - Inconsistent error message format for TypeError
The TypeError messages follow different patterns:
- `hello(None)` → "name must be a string, not None"
- `hello(123)` → "name must be a string, got int"

The "not None" phrasing is inconsistent with the "got {type}" pattern used for other non-string types.

### demo/hello.py - Unicode whitespace handling may be incomplete
The `str.strip()` method only strips ASCII whitespace by default. It does NOT strip all Unicode whitespace characters (e.g., non-breaking spaces `\u00A0`, thin space `\u2009`). This means Unicode whitespace won't be stripped properly for international users.

### tests/test_demo_hello.py - Missing __all__ test for package safety
The package defines `__all__` in both `demo/__init__.py` and `demo/hello.py` but there are no tests to verify that `from demo import *` only exports `hello` and that `__all__` is kept in sync with actual exports.

## Minor (nice to fix)

### tests/test_demo_hello.py:4 - Documentation inconsistency
Docstring states "8 tests total" but the file contains 11 tests. This should be updated for accuracy.

### demo/hello.py - Missing handling for string subclasses
The `isinstance(name, str)` check allows string subclasses, but `name.strip()` returns a base `str`, losing subclass information.

### demo/__main__.py - CLI accepts very long names without validation
The CLI passes any string from argparse directly to `hello()`. Extremely long names could cause memory pressure or terminal rendering issues.

## Warnings (follow-up ticket)

### demo/__main__.py - No handling for stdout write failures
The `print()` call could fail (e.g., broken pipe, disk full) but is not wrapped in a try-except.

### tests/test_demo_hello.py - Test comment says "8 tests total" but actual count is 11
Documentation drift in module docstring.

## Suggestions (follow-up ticket)

### demo/__main__.py - The argparse default value "World" is redundant
Since the `hello()` function already has a default parameter of "World", argparse default could be removed.

### demo/hello.py - Consider documenting type validation trade-off
The explicit type validation provides clearer error messages than Python's default TypeError, but is somewhat redundant with static type checking.

### tests/test_demo_hello.py - Add property-based tests
Consider using Hypothesis or similar for property-based testing to discover edge cases.

## Summary Statistics
- Critical: 0
- Major: 3
- Minor: 3
- Warnings: 2
- Suggestions: 6
