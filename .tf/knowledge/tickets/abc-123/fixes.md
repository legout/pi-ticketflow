# Fixes: abc-123

## Minor Issues Fixed

### 1. Use Sequence[str] instead of list[str] (reviewer-general)
**File:** `demo/__main__.py:21`

Changed `argv: Optional[list[str]]` to `argv: Optional[Sequence[str]]` to better express immutability intent. Also added import `from collections.abc import Sequence`.

### 2. Added empty string CLI example (reviewer-second-opinion)
**File:** `demo/__main__.py`

Added example to module docstring showing empty string behavior:
```
$ python -m demo ""
Hello, World!
```

## Issues Not Fixed (Intentional)

### CLI tests don't cover `if __name__ == "__main__"` block (Minor)
**Rationale:** Testing the `__main__` block requires subprocess spawning which adds complexity for minimal gain. The block is a simple `sys.exit(main())` wrapper that adds no additional logic.

## Summary
- Critical: 0 fixed
- Major: 0 fixed (already resolved in previous iteration)
- Minor: 2 fixed, 1 deferred
- Warnings: 0 fixed (become follow-up tickets)
- Suggestions: 0 fixed (become follow-up tickets)
