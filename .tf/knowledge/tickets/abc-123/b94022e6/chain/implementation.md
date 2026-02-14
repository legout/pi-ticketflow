# Implementation: abc-123

## Summary
Created a hello-world utility module (`demo/hello.py`) with CLI support (`demo/__main__.py`) to demonstrate the IRF workflow. The utility accepts a name parameter with default "World", includes comprehensive docstrings, and has 14 passing tests covering various edge cases.

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Files Changed
- `demo/__init__.py` - Module initialization with __all__ exports
- `demo/hello.py` - Main hello-world utility with hello() function and CLI support
- `demo/__main__.py` - CLI entry point with argparse
- `tests/test_demo_hello.py` - Comprehensive test suite (14 tests)

## Key Decisions
- Used argparse for CLI to follow project conventions
- Implemented whitespace stripping and Unicode whitespace handling
- Added type validation for None and non-string inputs
- Added BrokenPipeError handling for piped output
- Module-level regex compilation for performance

## Tests Run
- `pytest tests/test_demo_hello.py -v` - All 14 tests passing

## Verification
- All 14 tests passing
- Quality gate passed (0 Critical, 0 Major issues)
- Ticket closed successfully
