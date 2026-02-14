# Review: abc-123

## Critical (must fix)
No issues found.

## Major (should fix)
- `demo/hello.py:50` - **Unicode zero-width character handling bug**: `re.sub(r'[\s\u200B-\u200D\uFEFF]+', ' ', name)` replaces zero-width characters with a visible space. For inputs like `"Ali\u200Bce"`, output becomes `"Hello, Ali ce!"` instead of preserving `"Alice"`. This contradicts the docstring contract and produces incorrect user-visible names. *Sources: reviewer-general, reviewer-second-opinion*

- `demo/hello.py:38` - **Silent data loss risk**: The regex collapses ALL internal whitespace runs to single spaces. A user passing `hello("Alice    Bob")` (intentional multiple spaces) receives `"Hello, Alice Bob!"` without any indication that their data was modified. This violates POLS and could cause issues if names have legitimate spacing. *Source: reviewer-second-opinion*

- `demo/hello.py:35` - **Regex compiled on each call**: The regex pattern is recompiled on every function invocation. While minor for a hello utility, this sets a bad precedent. Consider module-level compilation: `_WHITESPACE_RE = re.compile(r'[\s\u200B-\u200D\uFEFF]+')`. *Source: reviewer-second-opinion*

- `demo/__main__.py:38` - **No BrokenPipeError handling**: `print(hello(args.name))` can raise `BrokenPipeError` if the output is piped and the reader closes early (e.g., `python -m demo | head -1`). This should be wrapped to catch BrokenPipeError and exit silently with code 0. *Source: reviewer-second-opinion*

## Minor (nice to fix)
- `tests/test_demo_hello.py:59` - Unicode tests cover leading/trailing and mixed whitespace cases, but not zero-width characters embedded inside words (e.g., `"Ali\u200Bce"`). This gap allowed the normalization bug to pass undetected. *Source: reviewer-general*

- `demo/hello.py:27-30` - **Docstring inaccuracy**: States "Empty strings and whitespace-only strings return the full greeting 'Hello, World!'" but the code actually returns this for ANY input that becomes empty after cleaning (e.g., `hello("\u200BWorld\u200B")` would return the default). *Source: reviewer-second-opinion*

- `tests/test_demo_hello.py:47` - **Incomplete Unicode coverage**: Tests zero-width chars but doesn't test other Unicode whitespace that `\s` matches differently across Python versions. Missing tests for `\xa0` (non-breaking space), `\u1680` (Ogham space mark), etc. *Source: reviewer-second-opinion*

- `demo/hello.py:33` - **Error message inconsistency**: `TypeError(f"name must be a string, got {type(name).__name__}")` produces messages like "got NoneType" which is less readable than "got None". Consider special-casing None. *Source: reviewer-second-opinion*

## Warnings (follow-up ticket)
- `demo/hello.py:41` - **API composability issue**: The function signature returns a full greeting, making it non-composable. `hello(hello("Alice"))` raises TypeError. Consider whether a `hello_raw()` function would be valuable. *Source: reviewer-second-opinion*

- `demo/__main__.py:25` - **No input length limit**: No validation on name length. Pathological inputs could cause memory pressure. Consider a reasonable max length (e.g., 1000 chars). *Source: reviewer-second-opinion*

## Suggestions (follow-up ticket)
- `demo/hello.py:50` - Consider separating normalization steps (remove zero-width chars first, then collapse whitespace) to make intent explicit and reduce future regressions. *Source: reviewer-general*

- Add a `strict: bool = False` parameter that, when True, preserves internal whitespace and only strips leading/trailing. *Source: reviewer-second-opinion*

- Consider exposing the cleaned name via a separate function for users who want the normalization logic without the greeting wrapper. *Source: reviewer-second-opinion*

## Positive Notes
- Excellent type annotations throughout with proper `from __future__ import annotations`
- Good use of `argparse` for CLI with proper help text and defaults
- Comprehensive test coverage including edge cases for Unicode and type validation
- Clean module structure with proper `__all__` exports
- Good input validation with explicit `TypeError` handling for non-string values
- CLI entry point is straightforward and test-covered

## Summary Statistics
- Critical: 0
- Major: 4
- Minor: 4
- Warnings: 2
- Suggestions: 3

## Reviewers
- reviewer-general: Major bug in Unicode handling identified
- reviewer-spec-audit: No issues found, implementation meets requirements
- reviewer-second-opinion: Multiple edge cases and design issues identified
