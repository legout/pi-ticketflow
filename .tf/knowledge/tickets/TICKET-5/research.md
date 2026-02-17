# Research: TICKET-5

## Status
Research complete. Implementation verified and ticket closed.

## Original Source
This ticket originated from the seed file:
- `.tf/knowledge/topics/seed-add-retry-logic-on-failed-tickets/seed.md`

## Vision from Seed
Implement retry logic for failed tickets in the Ralph loop:
- Detect prior attempts when tickets fail quality gate
- Increment retry counter per ticket
- Escalate to stronger models on retries
- Skip phases unlikely to help on retry (research, implementation if no changes)
- After N retries, mark as blocked and stop retrying

## Implementation Discovery
During implementation analysis, discovered that the retry logic feature was already extensively implemented in the codebase:

### Existing Implementation
1. **tf/retry_state.py** (583 lines)
   - `RetryState` class for state management
   - JSON persistence with atomic writes
   - Blocked status detection
   - Escalation model resolution

2. **tests/test_retry_state.py** (703 lines, 60 tests)
   - Comprehensive test coverage
   - All tests passing

3. **Integration Points**
   - `tf/implement.py` - Model escalation during implementation
   - `tf/close.py` - Retry state updates
   - `tf/ralph.py` - Max retries enforcement

4. **Configuration**
   - `.tf/config/settings.json` - Escalation schema
   - Disabled by default, opt-in

## Key Design Decisions (from existing code)

### State Location
- `{artifactDir}/retry-state.json` alongside other ticket artifacts
- Path: `.tf/knowledge/tickets/{ticket-id}/retry-state.json`

### Escalation Curve
| Attempt | Fixer | Reviewer-2nd | Worker |
|---------|-------|--------------|--------|
| 1 | Base | Base | Base |
| 2 | Escalated | Base | Base |
| 3+ | Escalated | Escalated | Escalated |

### Reset Policy
- Counter resets ONLY on successful close (CLOSED status)
- Use `--retry-reset` flag for manual reset

### Parallel Safety
- Warning logged when `parallelWorkers > 1`
- File locking not yet implemented (future enhancement)

## Schema

### Retry State (retry-state.json)
```json
{
  "version": 1,
  "ticketId": "pt-example",
  "attempts": [
    {
      "attemptNumber": 1,
      "startedAt": "2026-02-10T12:00:00Z",
      "completedAt": "2026-02-10T12:30:00Z",
      "status": "blocked",
      "trigger": "initial",
      "qualityGate": {
        "failOn": ["Critical", "Major"],
        "counts": {"Critical": 0, "Major": 2}
      },
      "escalation": {
        "fixer": null,
        "reviewerSecondOpinion": null,
        "worker": null
      }
    }
  ],
  "lastAttemptAt": "2026-02-10T12:30:00Z",
  "status": "blocked",
  "retryCount": 1
}
```

## Sources
- `.tf/knowledge/topics/seed-add-retry-logic-on-failed-tickets/seed.md`
- `tf/retry_state.py`
- `tests/test_retry_state.py`
- `tf/implement.py`
- `tf/close.py`
- `tf/ralph.py`
- `.tf/config/settings.json`
- `.tf/skills/tf-workflow/SKILL.md`
