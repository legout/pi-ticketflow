# Implementation: abc-123

## Summary
Hello-world utility module complete with CLI support. The implementation provides a simple greeting function that accepts a name parameter with proper edge case handling.

## Files Changed
- `demo/__init__.py` - Package initialization with exports
- `demo/hello.py` - Core greeting function with docstrings and type hints
- `demo/__main__.py` - CLI entry point using argparse
- `tests/test_demo_hello.py` - 6 unit tests covering functionality and edge cases

## Key Decisions
- Used `argparse` for CLI parsing per project convention
- Empty/whitespace strings fall back to "World" for robustness
- Added comprehensive docstrings with examples
- All functions have proper type annotations
- Used `from __future__ import annotations` for forward compatibility

## Tests Run
```
pytest tests/test_demo_hello.py -v
============================= 6 passed in 0.01s ==============================
```

Tests cover:
- Default parameter behavior
- Custom name input
- Empty string handling
- Whitespace-only string handling
- CLI default invocation
- CLI with name argument

## Verification
```bash
# Library usage
python3 -c "from demo.hello import hello; print(hello('Test'))"
# Output: Hello, Test!

# CLI usage
python3 -m demo Alice
# Output: Hello, Alice!
```
