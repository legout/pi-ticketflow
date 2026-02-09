# Implementation: abc-123

## Summary
Created a simple hello-world utility module in `demo/hello.py` with comprehensive tests in `tests/test_demo_hello.py`. The implementation fulfills all acceptance criteria from the ticket.

## Files Changed
- `demo/__init__.py` - Package init (created/updated)
- `demo/hello.py` - Hello-world utility with typed function
- `tests/test_demo_hello.py` - Unit tests (3 test cases)

## Key Decisions
- Used simple function design with default parameter `name: str = "World"`
- Added type hints for better code quality
- Included comprehensive docstring following Google style
- Added edge case test for empty string

## Tests Run
```bash
python -m pytest tests/test_demo_hello.py -v
```

Results: 3 passed
- test_hello_default - Verifies default "World" greeting
- test_hello_custom_name - Verifies custom name works
- test_hello_empty_string - Edge case handling

## Verification
The utility can be run directly:
```bash
python -m demo.hello
# Output: Hello, World!

python -c "from demo.hello import hello; print(hello('Pi'))"
# Output: Hello, Pi!
```
