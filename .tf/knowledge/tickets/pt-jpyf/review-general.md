# Review: pt-jpyf

## Overall Assessment
The implementation correctly adds session finalization logic to `/tf-backlog` with proper handling of success and error cases. The code integrates well with the existing session lifecycle defined in `/tf-seed` and follows the established patterns for session state management.

## Critical (must fix)
- `prompts/tf-backlog.md:11` - **Session finalization only happens in Step 11, but partial failures during ticket creation (steps 5-7) may leave inconsistent state**: The error handling states "If ticket creation fails part-way through, do NOT remove `.active-planning.json`" but there's no explicit logic showing where this error detection happens between steps 5-7 and step 11. The flow assumes all tickets succeed or fail atomically, but `tk create` is called in a loop - individual failures could occur.

## Major (should fix)
- `prompts/tf-backlog.md:113-127` - **Session finalization writes to `sessions/{session_id}.json` but session retrieval may fail if directory doesn't exist**: The session file path assumes `sessions/` directory exists, but there's no explicit `mkdir -p` step shown. If a user manually creates `.active-planning.json` or the directory was deleted, this will fail.
- `prompts/tf-backlog.md:113` - **Session snapshot schema mismatch with `/tf-seed` session format**: The schema includes `spikes`, `plan`, and `backlog` fields in the final snapshot, but `/tf-seed.md` doesn't document what fields are accumulated during the session lifecycle. Need to verify if spikes and plan are actually captured during session progression or if this is aspirational.

## Minor (nice to fix)
- `prompts/tf-backlog.md:107-109` - **Error handling description is vague**: "Write error note to session snapshot" doesn't specify the format or structure of the error note. Should define a schema (e.g., `{ "error": { "message": "...", "failed_at": "step", "tickets_created": [...] } }`).
- `prompts/tf-backlog.md:11` - **Session detection happens at start but there's no validation of session state**: The check is for `state: active` but doesn't handle cases where session file exists with other states (e.g., `archived`, `completed` from a previous run).

## Warnings (follow-up ticket)
- `prompts/tf-backlog.md:131` - **`--links-only` mode explicitly does NOT finalize sessions, but there's no warning emitted**: Users might expect session completion after running `--links-only` followed by normal backlog generation. Consider emitting a notice: "[tf] Session remains active (use --links-only after full backlog to complete)".
- `prompts/tf-backlog.md:113-127` - **Session snapshots accumulate but there's no cleanup mechanism**: Over time `sessions/` directory could grow large. Consider a retention policy or archival mechanism in a follow-up.

## Suggestions (follow-up ticket)
- `prompts/tf-backlog.md:127` - **Session finalization notice could include backlog path**: Current notice is `[tf] Session finalized: {session_id} ({count} tickets created)`. Consider adding backlog location: `[tf] Session finalized: {session_id} ({count} tickets, {backlog_path})`.
- `prompts/tf-backlog.md` - **Consider adding a session verification subcommand**: A `/tf-seed --verify` or similar could validate that `.active-planning.json` points to valid session files and report any inconsistencies.
- `prompts/tf-backlog.md:11` - **Session handling could be extracted to a shared include**: Both `/tf-seed` and `/tf-backlog` now manage sessions; consider a shared session management utility or skill to avoid duplication and drift.

## Positive Notes
- **Clear separation of concerns**: Session handling is clearly marked in both the Execution section and Output section, making it easy to understand the behavior.
- **Good error handling philosophy**: Not deleting the active pointer on failure is the right choice - allows for retry without losing session context.
- **Consistent with existing patterns**: The session ID format (`{seed-id}@{timestamp}`) matches `/tf-seed` conventions, and the JSON schema follows the established pattern with `schema_version`.
- **Well-documented edge cases**: The `--links-only` exception is clearly called out in both the Execution steps and Output sections.
- **Acceptance criteria fully addressed**: All 5 acceptance criteria from the implementation are met: backlog metadata recording, completed snapshot, active pointer removal, notice emission, and partial failure handling.

## Summary Statistics
- Critical: 1
- Major: 2
- Minor: 2
- Warnings: 2
- Suggestions: 3
