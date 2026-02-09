# Implementation: abc-123

## Summary
Created a simple hello-world utility module (`demo/hello.py`) with proper Python structure, docstrings, and comprehensive tests.

## Files Changed
- `demo/__init__.py` - Package initialization exposing `hello` function
- `demo/hello.py` - Main hello-world utility with `hello(name="World")` function
- `tests/test_demo_hello.py` - Test suite with 3 test cases

## Key Decisions
- Used a separate `demo/` directory at project root for clarity
- Implemented type hints for better code quality
- Included comprehensive docstrings following PEP 257
- Created 3 test cases covering default, custom, and edge cases

## Tests Run
```bash
python -m pytest tests/test_demo_hello.py -v
```
Result: 3 passed in 0.02s

## Verification
- Run `python demo/hello.py` to see default greeting
- Run `python -c "from demo.hello import hello; print(hello('Test'))"` for custom greeting
- All tests pass successfully
