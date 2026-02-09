# Fixes: abc-123

## Issues Fixed

### Major (1 fixed)
1. **RuntimeWarning on CLI execution** (`demo/hello.py`)
   - Created `demo/__main__.py` as proper CLI entry point
   - Eliminates "found in sys.modules after import" warning
   - New usage: `python -m demo [name]` instead of `python -m demo.hello [name]`

### Minor (1 fixed)
1. **Pythonic CLI handling** (`demo/hello.py:43`)
   - Changed `name = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "World"`
   - To: `name = " ".join(sys.argv[1:]) or "World"`
   - Uses Python's short-circuit evaluation for cleaner code

### Minor (1 deferred - not fixed)
- Empty string test behavior - intentionally not fixed as it's valid edge case behavior; function contract allows empty strings

## Files Changed
- `demo/hello.py` - Simplified CLI argument handling
- `demo/__main__.py` - Created new CLI entry point

## Verification
- All 3 tests pass: `python -m pytest tests/test_demo_hello.py -v`
- CLI works without warning: `python -m demo TestUser` → "Hello, TestUser!"
- Backward compatibility: `python -m demo.hello Test` still works (with expected warning)
