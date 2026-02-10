# Fixes: pt-tl00

## Summary
Fixed bug in `is_ticket_blocked_by_retries()` where aggregate status was checked instead of last attempt status.

## Fixes by Severity

### Critical (must fix)
- [x] Fixed `is_ticket_blocked_by_retries()` in `tf/ralph.py` - Changed from checking `retry_state.get("status") == "blocked"` to checking `last_attempt.get("status") == "blocked"`

### Major (should fix)
- None

### Minor (nice to fix)
- None

### Warnings (follow-up)
- None

### Suggestions (follow-up)
- None

## Summary Statistics
- **Critical**: 1 fixed
- **Major**: 0
- **Minor**: 0
- **Warnings**: 0
- **Suggestions**: 0

## Verification
- All 60 retry state tests pass
- Integration test verified correct behavior for:
  - Ticket at max retries (correctly blocked)
  - Ticket below max retries (correctly allowed)
  - Counter reset after successful close
  - New ticket with no state
