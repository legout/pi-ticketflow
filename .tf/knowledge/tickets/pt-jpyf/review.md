# Review: pt-jpyf

## Critical (must fix)

### 1. State naming inconsistency (review-second)
- **Location**: `prompts/tf-backlog.md:11`
- **Issue**: The implementation specifies `state: completed` but existing session convention uses `state: archived` (see `.tf/knowledge/sessions/*.json`). This creates dual-state confusion.
- **Fix**: Use `state: archived` for consistency with existing `/tf-seed` behavior.

### 2. Partial failure detection (review-general)
- **Location**: `prompts/tf-backlog.md:11`
- **Issue**: Error handling states "If ticket creation fails part-way through, do NOT remove `.active-planning.json`" but there's no explicit logic showing where error detection happens between steps 5-7 and step 11.
- **Fix**: Add explicit error tracking during ticket creation loop.

## Major (should fix)

### 3. Missing sessions directory handling (review-general)
- **Location**: `prompts/tf-backlog.md:113-127`
- **Issue**: Session file path assumes `sessions/` directory exists, but no `mkdir -p` step shown.
- **Fix**: Add `mkdir -p .tf/knowledge/sessions` before writing snapshot.

### 4. Missing `updated` timestamp (review-second)
- **Location**: `prompts/tf-backlog.md:11`
- **Issue**: Session finalization writes `completed_at` but doesn't update the `updated` field.
- **Fix**: Update `updated` field to finalization timestamp.

### 5. Unclear error note specification (review-second)
- **Location**: `prompts/tf-backlog.md:11`
- **Issue**: "Write error note to session snapshot" doesn't specify WHERE in JSON structure.
- **Fix**: Define explicit error schema with `error.message`, `error.failed_at`, `error.tickets_created`.

### 6. Zero-tickets edge case (review-second)
- **Location**: `prompts/tf-backlog.md:11`
- **Issue**: Finalization logic doesn't handle case where 0 tickets created (all duplicates).
- **Fix**: Add explicit handling for zero tickets - still finalize but with clear messaging.

## Minor (nice to fix)

### 7. Error handling description vagueness (review-general)
- **Location**: `prompts/tf-backlog.md:107-109`
- **Issue**: Error handling description doesn't specify format of error note.
- **Fix**: Already covered by fix #5 above.

### 8. Session state validation (review-general)
- **Location**: `prompts/tf-backlog.md:11`
- **Issue**: Check is for `state: active` but doesn't handle other states (archived, completed).
- **Fix**: Add validation that only processes `state: active` sessions.

## Summary Statistics
- Critical: 2
- Major: 4
- Minor: 2
- Warnings: 4
- Suggestions: 7

## Spec Compliance
✅ All acceptance criteria from ticket are addressed:
- Records `backlog.topic`, `backlog.backlog_md`, and `backlog.tickets`
- Writes session snapshot with terminal state + `completed_at`
- Removes `.active-planning.json`
- Emits one-line notice
- Handles partial failures without deleting active pointer
