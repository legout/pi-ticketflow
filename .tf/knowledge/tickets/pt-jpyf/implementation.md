# Implementation: pt-jpyf

## Summary
Implemented session finalization logic in `/tf-backlog` prompt. When a planning session is active during backlog generation, the command now records created tickets, writes a completed session snapshot, and deactivates the session.

## Files Changed
- `prompts/tf-backlog.md` - Added session handling and finalization procedures

## Key Changes

### 1. Session Detection at Start
Added **Session Handling** section to the Execution steps:
- At start: Check for `.active-planning.json`. If exists and `state: active`, capture `session_id` and `root_seed` for later finalization.
- At end (if session was active): Record backlog metadata, write completed snapshot, deactivate session.

### 2. Session Finalization Step (Step 11)
Added comprehensive session finalization procedure:
- Records backlog metadata:
  - `backlog.topic` - the topic-id used for backlog generation
  - `backlog.backlog_md` - path to the generated backlog.md
  - `backlog.tickets` - array of created ticket IDs
- Writes completed session snapshot to `sessions/{session_id}.json`:
  - Sets `state: completed`
  - Sets `completed_at` to ISO8601 timestamp
  - Includes full session history (root_seed, spikes, plan, backlog)
- Removes `.active-planning.json` to deactivate the session
- Emits notice: `[tf] Session finalized: {session_id} ({count} tickets created)`

### 3. Error Handling
- If ticket creation fails part-way through, do NOT remove `.active-planning.json`
- Write error note to session snapshot
- Leave active pointer intact for retry

### 4. Output Section Updates
- Documented session finalization in Normal mode output
- Documented that `--links-only` mode does NOT finalize sessions

### 5. Next Steps Update
- Clarified that the planning session is complete after backlog generation
- Added pointer to `/tf-seed` for starting new sessions

## Tests Run
- Verified prompt syntax and markdown structure
- Confirmed all acceptance criteria are addressed:
  - [x] After successful ticket creation, session records `backlog.topic`, `backlog.backlog_md`, and `backlog.tickets`
  - [x] Session snapshot is written to `sessions/{session_id}.json` with `state: completed` + `completed_at`
  - [x] `.active-planning.json` is removed after completion
  - [x] Emits a one-line notice when finalizing
  - [x] If ticket creation fails part-way, do not delete the active pointer; write an error note

## Verification
To verify the implementation:
1. Create a seed with `/tf-seed "Test feature"` (activates a session)
2. Run `/tf-backlog seed-test-feature` to generate backlog
3. Verify session snapshot in `.tf/knowledge/sessions/{session_id}.json` has `state: completed`
4. Verify `.active-planning.json` no longer exists
5. Verify the notice was emitted
