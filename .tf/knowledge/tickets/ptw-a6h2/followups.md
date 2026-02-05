# Follow-up Tickets: ptw-a6h2

## Created Follow-up Tickets

### Warnings Addressed

1. **ptw-o0ng** - Add `from __future__ import annotations` to tf_cli modules
   - Rationale: Forward compatibility with Python 3.9+ type hints
   - Scope: All modules in tf_cli package

2. **ptw-7zri** - Optimize normalize_version performance
   - Rationale: Use `version.startswith(('v', 'V'))` instead of `version.lower().startswith("v")`
   - Avoids creating lowercase copy of entire string

3. **ptw-0un2** - Add pytest coverage configuration
   - Rationale: Track overall test coverage goals
   - Suggestion: Fail if coverage < 80%

4. **ptw-ykvx** - Add integration tests for version check in run_doctor CLI flow
   - Rationale: Verify end-to-end interaction between functions
   - Test that check_version_consistency is called with correct arguments

## Warnings Deferred

The following warnings were noted but not ticketed as they are lower priority:
- Import path verification for CI (assumes editable install)
- Additional pathological input tests (None, unicode, concurrent access)

## Suggestions Deferred

The following suggestions were noted for future consideration:
- Extract test data into module-level constants
- Add conftest.py with shared fixtures
- Consider returning enum (CREATED/UPDATED/UNCHANGED/FAILED) from sync_version_file
- Add module-level docstrings to other test files

## Summary
- Created: 4 follow-up tickets
- Deferred: 4 warnings/suggestions (lower priority or architectural)
