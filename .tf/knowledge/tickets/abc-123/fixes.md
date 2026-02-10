# Fixes: abc-123

## Summary
Applied 1 Minor fix from review feedback.

## Fixes Applied

### Minor Fix
- `demo/__main__.py:16,20` - Modernized type hint
  - Changed: `from typing import Optional` → removed import
  - Changed: `Optional[Sequence[str]]` → `Sequence[str] | None`
  - Reason: `Optional` is deprecated since Python 3.10, union syntax is preferred
  - File already had `from __future__ import annotations` enabling modern syntax

## Verification
- All 8 tests passing after fix
- CLI functionality verified: `python -m demo` works correctly

## Files Modified
- `demo/__main__.py`
