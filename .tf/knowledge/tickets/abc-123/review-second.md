# Review: abc-123

## Overall Assessment
The implementation is solid and well-tested, but several edge cases around Unicode handling, silent data loss, and API design could cause subtle bugs in production usage. The aggressive whitespace normalization may violate the principle of least surprise.

## Critical (must fix)
No issues found.

## Major (should fix)
- `demo/hello.py:38` - **Silent data loss risk**: The regex `re.sub(r'[\s\u200B-\u200D\uFEFF]+', ' ', name)` collapses ALL internal whitespace runs to single spaces. A user passing `hello("Alice    Bob")` (intentional multiple spaces) receives `"Hello, Alice Bob!"` without any indication that their data was modified. This violates POLS and could cause issues if names have legitimate spacing (e.g., formatted titles, aligned text).

- `demo/hello.py:35` - **Regex compiled on each call**: The regex pattern is recompiled on every function invocation. While minor for a hello utility, this sets a bad precedent and has O(n) overhead per call. Consider module-level compilation: `_WHITESPACE_RE = re.compile(r'[\s\u200B-\u200D\uFEFF]+')`.

- `demo/__main__.py:38` - **No error handling for stdout**: `print(hello(args.name))` can raise `BrokenPipeError` if the output is piped and the reader closes early (e.g., `python -m demo | head -1`). This should be wrapped to catch BrokenPipeError and exit silently with code 0.

## Minor (nice to fix)
- `demo/hello.py:27-30` - **Docstring inaccuracy**: States "Empty strings and whitespace-only strings return the full greeting 'Hello, World!'" but the code actually returns this for ANY input that becomes empty after cleaning (e.g., `hello("\u200BWorld\u200B")` with zero-width chars would return the default, not "Hello, World!"). The documentation is slightly misleading.

- `tests/test_demo_hello.py:47` - **Incomplete Unicode coverage**: Tests zero-width chars but doesn't test other Unicode whitespace that `\s` matches differently across Python versions or regex modes. Missing tests for `\xa0` (non-breaking space), `\u1680` (Ogham space mark), etc.

- `demo/hello.py:33` - **Error message inconsistency**: `TypeError(f"name must be a string, got {type(name).__name__}")` produces messages like "got NoneType" which is technically correct but less readable than "got None". Consider special-casing None: `type(name).__name__ if name is not None else "None"`.

## Warnings (follow-up ticket)
- `demo/hello.py:41` - **API composability issue**: The function signature `hello(name: str = "World") -> str` returns a full greeting, making it non-composable. `hello(hello("Alice"))` raises TypeError. Consider whether a `hello_raw()` function that returns just the cleaned name would be valuable for chaining.

- `demo/__main__.py:25` - **No input length limit**: No validation on name length. Pathological inputs like `python -m demo $(python -c "print('A'*10000000)")` could cause memory pressure. Consider a reasonable max length (e.g., 1000 chars).

## Suggestions (follow-up ticket)
- Add a `strict: bool = False` parameter that, when True, preserves internal whitespace and only strips leading/trailing. This would give users control over the data-loss behavior.

- Consider exposing the cleaned name via a separate function for users who want the normalization logic without the greeting wrapper.

- Add a test for the BrokenPipeError scenario using `pytest` monkeypatch or subprocess testing.

## Positive Notes
- Excellent type annotations throughout with proper `from __future__ import annotations`
- Good use of `argparse` for CLI with proper help text and defaults
- Comprehensive test coverage including edge cases for Unicode and type validation
- Clean module structure with proper `__all__` exports
- Tests verify both the library API and CLI entry point

## Summary Statistics
- Critical: 0
- Major: 3
- Minor: 3
- Warnings: 2
- Suggestions: 3
