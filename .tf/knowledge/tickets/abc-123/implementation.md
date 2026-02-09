# Implementation: abc-123

## Summary
Hello-world utility module created in `demo/` package with CLI support and comprehensive tests.

## Files Changed
- `demo/__init__.py` - Package init, exports `hello`
- `demo/hello.py` - Main greeting function with docstring
- `demo/__main__.py` - CLI entry point
- `tests/test_demo_hello.py` - Unit tests (3 tests)

## Key Decisions
- Used `from __future__ import annotations` for consistency
- CLI handles multi-word names via `" ".join(sys.argv[1:]).strip()`
- Added pytestmark for unit test categorization
- Module docstring includes examples and CLI usage

## Tests Run
```bash
python -m pytest tests/test_demo_hello.py -v
# 3 passed in 0.02s
```

## Verification
```bash
python -c "from demo.hello import hello; print(hello())"
# Hello, World!

python -m demo Alice
# Hello, Alice!
```
