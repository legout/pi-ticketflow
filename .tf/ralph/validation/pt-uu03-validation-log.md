# Validation Matrix for pt-uu03

**Date**: 2026-02-14T02:00:40Z
**Ticket**: pt-uu03 - Run manual validation matrix for dispatch Ralph mode
**Validator**: Ralph (autonomous)

---

## Acceptance Criteria

1. [ ] Serial dispatch run validated end-to-end on at least one ticket
2. [ ] Parallel dispatch run validated with non-overlapping component tags
3. [ ] Fallback `--no-interactive-shell` path validated
4. [ ] Timeout/orphan recovery scenarios validated and logged

---

## Test Environment

- **Ralph CLI version**: `tf ralph --version`
- **Pi version**: `pi --version`
- **Repository**: pi-ticketflow
- **Worktrees root**: `.tf/ralph/worktrees/`

---

## Test 1: Serial Dispatch Run End-to-End

**Objective**: Validate that `tf ralph run <ticket>` uses dispatch mode by default and completes successfully.

### Pre-conditions
- [ ] No existing sessions running (or orphaned sessions cleaned)
- [ ] Ticket in ready state

### Steps
1. Run `tf ralph run <ticket> --verbose`
2. Observe session creation in dispatch-sessions.json
3. Verify worktree creation
4. Verify session completion
5. Verify progress.md updated
6. Verify lessons extracted to AGENTS.md

### Results
_To be filled during testing_

---

## Test 2: Parallel Dispatch Run

**Objective**: Validate `tf ralph start --parallel N` with non-overlapping component tags.

### Pre-conditions
- [ ] Multiple tickets ready with different component tags
- [ ] No conflicting dependencies

### Steps
1. Run `tf ralph start --parallel 2 --max-iterations 4`
2. Observe multiple sessions created
3. Verify component tag isolation
4. Verify both sessions complete
5. Verify progress.md updated for both

### Results
_To be filled during testing_

---

## Test 3: Fallback `--no-interactive-shell` Path

**Objective**: Validate legacy subprocess backend works correctly.

### Pre-conditions
- [ ] Ticket in ready state

### Steps
1. Run `tf ralph run <ticket> --no-interactive-shell --verbose`
2. Verify subprocess backend used (not dispatch)
3. Verify completion detection
4. Verify progress.md updated

### Results
_To be filled during testing_

---

## Test 4: Timeout/Orphan Recovery

**Objective**: Validate timeout handling and orphaned session cleanup.

### Sub-test 4a: Timeout Detection
1. Configure short timeout (e.g., 5000ms)
2. Run `tf ralph run <ticket> --verbose`
3. Verify timeout detected
4. Verify session killed
5. Verify session marked as failed

### Sub-test 4b: Orphan Recovery
1. Create orphaned session state
2. Run `tf ralph run <ticket> --verbose` (triggers startup recovery)
3. Verify orphaned sessions detected
4. Verify orphaned sessions cleaned up
5. Verify worktree removed

### Results
_To be filled during testing_

---

## Summary

| Test | Status | Notes |
|------|--------|-------|
| Serial Dispatch | PENDING | |
| Parallel Dispatch | PENDING | |
| Fallback Subprocess | PENDING | |
| Timeout Recovery | PENDING | |
| Orphan Recovery | PENDING | |

---

## Issues Found

_If any issues are discovered during validation, document them here._

