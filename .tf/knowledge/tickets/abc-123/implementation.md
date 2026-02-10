# Implementation: abc-123

## Summary
Hello-world utility module for demonstrating the IRF workflow. The implementation includes a greeting function with CLI support, comprehensive test coverage, and proper Python packaging.

**Re-verification run** - Ticket was previously closed, this is a workflow re-execution with --auto flag.

## Retry Context
- Attempt: 1 (fresh re-verification)
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Files Changed
- `demo/hello.py` - Core greeting function with docstring and type hints
- `demo/__main__.py` - CLI entry point using argparse
- `demo/__init__.py` - Package initialization
- `tests/test_demo_hello.py` - Test suite with 8 tests covering all edge cases

## Key Decisions
- Used `argparse` for CLI handling (project convention)
- Whitespace stripping in `hello()` ensures consistent output
- Empty/whitespace-only strings fall back to "World" greeting
- Added comprehensive edge case tests (whitespace variations, empty strings)
- All functions have proper docstrings with Google-style formatting

## Tests Run
```bash
python -m pytest tests/test_demo_hello.py -v
```
Results: **8 passed** in 0.03s

### Test Coverage
- `test_hello_default` - Default parameter behavior
- `test_hello_custom_name` - Custom name greeting
- `test_hello_empty_string` - Empty string handling
- `test_hello_whitespace_only` - Whitespace-only string handling
- `test_hello_whitespace_stripped` - Leading/trailing whitespace stripping
- `test_cli_default` - CLI with no arguments
- `test_cli_with_name` - CLI with name argument
- `test_cli_empty_string` - CLI with empty string argument

## Verification
Run the module directly:
```bash
python -m demo          # Hello, World!
python -m demo Alice    # Hello, Alice!
```

Or import as library:
```python
from demo.hello import hello
hello("World")  # "Hello, World!"
```

## Quality Checks
- Tests: ✅ 8/8 passing
- Lint: ⚠️ Skipped (ruff not available)
- Format: ⚠️ Skipped (ruff not available)
