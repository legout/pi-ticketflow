# Fixes: abc-123

## Issues Fixed

### Minor
- `tests/test_demo_hello.py:3` - Corrected module docstring from "(6 tests total)" to "(8 tests total)" to match actual test count.

## Issues Not Fixed (Intentional)

### Minor
- `pyproject.toml` demo package inclusion - This is a project-level decision about whether demo packages belong in distribution. Not a code issue.

### Warnings (Follow-up tickets)
- Tooling (ruff) missing - Requires environment setup, not code change.
- Type checking not performed - Requires CI/pipeline changes, not code change.

### Suggestions (Follow-up tickets)
- Runtime type validation, py.typed marker, Hypothesis tests, Unicode tests, CLI --version flag, README examples - All are enhancements for future tickets, not required fixes.

## Verification
Tests re-run after fix: **8 passed** ✅
