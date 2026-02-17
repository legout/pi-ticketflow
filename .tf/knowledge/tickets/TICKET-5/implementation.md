# Implementation: TICKET-5

## Summary
Implemented retry logic for failed tickets with model escalation support. When tickets fail quality gate checks (blocked status), the workflow now detects prior attempts, increments a retry counter, and escalates to stronger models on subsequent retries.

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Files Changed

### Core Implementation
- `tf/retry_state.py` (583 lines) - Complete retry state management module
  - `RetryState` class for load/save/tracking
  - Blocked status detection from close-summary.md and review.md
  - Escalation model resolution based on attempt number
  - JSON persistence with atomic writes

### Integration Points
- `tf/implement.py` - Uses retry state for model resolution during implementation
- `tf/close.py` - Updates retry state on ticket close/complete
- `tf/ralph.py` - Checks max_retries before processing tickets in loop

### Configuration
- `.tf/config/settings.json` - Added `workflow.escalation` section:
  ```json
  "escalation": {
    "enabled": false,
    "maxRetries": 3,
    "models": {
      "fixer": null,
      "reviewerSecondOpinion": null,
      "worker": null
    }
  }
  ```

### Tests
- `tests/test_retry_state.py` (703 lines) - Comprehensive test coverage
  - State persistence tests
  - Retry counter behavior
  - Escalation model resolution
  - Blocked status detection
  - Edge cases and error handling

## Key Features Implemented

### 1. Retry State Schema (retry-state.json)
```json
{
  "version": 1,
  "ticketId": "pt-example",
  "attempts": [...],
  "lastAttemptAt": "...",
  "status": "active|blocked|closed",
  "retryCount": 0
}
```

### 2. Escalation Curve
| Attempt | Fixer | Reviewer-2nd-Opinion | Worker |
|---------|-------|---------------------|--------|
| 1 (fresh) | Base | Base | Base |
| 2 (retry) | Escalated | Base | Base |
| 3+ (subsequent) | Escalated | Escalated | Escalated |

### 3. Ralph Integration
- Checks `retryCount >= maxRetries` before processing
- Skips tickets that have exceeded max retries
- Logs retry status in progress output

### 4. Phase Adaptation
- Research phase: Skipped on retries (configurable via flags)
- Implementation: Uses escalated worker models on attempt 3+
- Reviews: Uses escalated second-opinion model on attempt 3+
- Fix: Uses escalated fixer model on attempt 2+

## Key Decisions

1. **State Location**: `{artifactDir}/retry-state.json` alongside other ticket artifacts
2. **Reset Policy**: Counter resets only on successful close (CLOSED status)
3. **Atomic Writes**: Uses temp file + rename for safe persistence
4. **Parallel Safety**: Warns when parallelWorkers > 1 (file locking not yet implemented)
5. **Backward Compatible**: Escalation disabled by default; opt-in via settings

## Tests Run

```bash
$ python -m pytest tests/test_retry_state.py -v
============================= test results =============================
PASSED tests/test_retry_state.py::TestRetryStatePersistence::test_load_nonexistent_file
PASSED tests/test_retry_state.py::TestRetryStatePersistence::test_load_invalid_json
PASSED tests/test_retry_state.py::TestRetryStatePersistence::test_load_missing_required_fields
PASSED tests/test_retry_state.py::TestRetryStatePersistence::test_load_valid_state
PASSED tests/test_retry_state.py::TestRetryStatePersistence::test_save_creates_directory
PASSED tests/test_retry_state.py::TestRetryStatePersistence::test_save_and_load_roundtrip
PASSED tests/test_retry_state.py::TestRetryStatePersistence::test_atomic_save
PASSED tests/test_retry_state.py::TestRetryCounter::test_initial_retry_count
PASSED tests/test_retry_state.py::TestRetryCounter::test_retry_count_increments_on_blocked
PASSED tests/test_retry_state.py::TestRetryCounter::test_retry_count_increments_multiple_blocked
PASSED tests/test_retry_state.py::TestRetryCounter::test_retry_count_resets_on_closed
PASSED tests/test_retry_state.py::TestRetryCounter::test_attempt_number_tracking
PASSED tests/test_retry_state.py::TestBlockedDetection::test_detect_blocked_from_close_summary
PASSED tests/test_retry_state.py::TestBlockedDetection::test_detect_blocked_from_review
PASSED tests/test_retry_state.py::TestBlockedDetection::test_detect_quality_gate_blocked
PASSED tests/test_retry_state.py::TestBlockedDetection::test_detect_close_status
PASSED tests/test_retry_state.py::TestEscalationResolution::test_escalation_disabled
PASSED tests/test_retry_state.py::TestEscalationResolution::test_escalation_attempt_1_no_escalation
PASSED tests/test_retry_state.py::TestEscalationResolution::test_escalation_attempt_2_fixer_only
PASSED tests/test_retry_state.py::TestEscalationResolution::test_escalation_attempt_3_all_models
PASSED tests/test_retry_state.py::TestEscalationResolution::test_escalation_with_explicit_models
PASSED tests/test_retry_state.py::TestEscalationConfig::test_load_escalation_config_defaults
PASSED tests/test_retry_state.py::TestEscalationConfig::test_load_escalation_config_from_settings
PASSED tests/test_retry_state.py::TestIntegration::test_full_retry_lifecycle
============================== 24 passed ==============================
```

## Verification

1. **Enable escalation** in `.tf/config/settings.json`:
   ```json
   "escalation": {
     "enabled": true,
     "maxRetries": 3,
     "models": {
       "fixer": "openai-codex/gpt-5.3-codex",
       "reviewerSecondOpinion": "openai-codex/gpt-5.3-codex",
       "worker": null
     }
   }
   ```

2. **Run Ralph** with escalation enabled - blocked tickets will retry with escalated models

3. **Check retry state** in `.tf/knowledge/tickets/{ticket-id}/retry-state.json`

## Compliance with Seed Requirements

✅ **Retry counter**: Persisted per ticket across Ralph iterations  
✅ **Escalation config**: Configurable models for each role  
✅ **Phase adaptation**: Focus on review+fix on retries  
✅ **Convergence**: Max retries enforcement with skip behavior  
✅ **Auditability**: Artifacts document escalation decisions  

## Open Questions Addressed

1. **State location**: Ticket artifacts directory (`{artifactDir}/`)
2. **Applies to**: Both Ralph and `/tf` manual runs
3. **Post-fix re-review**: Handled by existing quality gate system
4. **Default policy**: Disabled by default (opt-in), maxRetries=3
5. **Decision stability**: State persists across runs, only reset on success
