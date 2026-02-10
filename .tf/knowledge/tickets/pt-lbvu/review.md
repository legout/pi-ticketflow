# Review: pt-lbvu

## Critical (must fix)
- No issues found

## Major (should fix)
- [x] `tf/retry_state.py:603-633` - `load_escalation_config()` silently swallows all `IOError` exceptions including permission errors, potentially masking configuration issues where the file exists but isn't readable (wrong permissions, locked file).
  - Source: reviewer-second-opinion
  - Fixed: Distinguished `PermissionError` from `IOError` and logs permission errors at ERROR level for visibility

## Minor (nice to fix)
- `tf/retry_state.py:388-401` - `resolve_escalation()` accepts negative or zero `next_attempt_number` without validation, which could produce unexpected escalation behavior if called with erroneous parameters.
  - Source: reviewer-second-opinion
- `tf/retry_state.py:398-401` - The worker escalation logic is asymmetric: worker only escalates on attempt 3+ if explicitly configured (non-null), while fixer and reviewer fall back to base models. This subtle difference isn't highlighted in docs.
  - Source: reviewer-second-opinion
- `docs/configuration.md:254-270` - The escalation curve table shows "Escalation model (if configured)" for worker at attempt 3+, but this phrasing understates the behavioral difference - worker escalation is opt-in while others are fallback-based.
  - Source: reviewer-second-opinion
- `.tf/config/settings.json:126-134` - All escalation models are `null` by default, which is correct for backwards compatibility, but means escalation is effectively a no-op until explicitly configured - this could confuse users who enable `enabled: true` without setting models.
  - Source: reviewer-second-opinion

## Warnings (follow-up ticket)
- `tf/retry_state.py:25-34` - `DEFAULT_ESCALATION_CONFIG` uses `dict[str, Any]` typing which bypasses type checking. Consider using `TypedDict` for stricter validation, especially since nested `models` dict merging relies on structure.
  - Source: reviewer-second-opinion
- `tf/retry_state.py:234-247` - The schema validation in `_validate_schema()` only checks field existence, not types or values (e.g., `version` could be a string, `retryCount` could be negative).
  - Source: reviewer-second-opinion

## Suggestions (follow-up ticket)
- Add a config validation warning when `escalation.enabled: true` but all models are null - help users discover they need to configure models.
  - Source: reviewer-second-opinion
- Consider adding `attempt 4+` behavior documentation - current docs imply the curve plateaus at attempt 3 but don't explicitly state what happens beyond.
  - Source: reviewer-second-opinion
- Add test case for `next_attempt_number=0` in `resolve_escalation()` to document/verify expected behavior.
  - Source: reviewer-second-opinion

## Summary Statistics
- Critical: 0
- Major: 0
- Minor: 4
- Warnings: 2
- Suggestions: 3
