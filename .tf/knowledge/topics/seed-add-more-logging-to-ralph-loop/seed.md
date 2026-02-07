# Seed: Add more logging to the Ralph loop (tk ralph start/run)

## Vision
When Ralph runs autonomously, failures can be hard to diagnose from the outside (e.g., “what ticket was it on?”, “which phase failed?”, “what command/tool caused it?”). Better logs should make the loop understandable and debuggable during normal operation.

## Core Concept
Add additional, consistent logging at key lifecycle points of the Ralph loop when run via `tk ralph start` or `tk ralph run` (or their `tf` equivalents), including:
- loop start/end
- ticket selection decisions
- phase transitions (re-anchor → research → implement → review → fix → close)
- tool/command execution boundaries
- error summaries with context pointers (ticket id, artifact paths)

Prefer structured logs (or at least consistently formatted lines) that are both human-readable and greppable.

## Key Features
1. **Lifecycle logging**: start/end + per-iteration markers with timestamps.
2. **Ticket-level context**: always include ticket ID and current phase.
3. **Decision logging**: why a ticket was selected/skipped (deps blocked, not ready, etc.).
4. **Error reporting**: concise error summary + where to look next (artifact dir, failing command).
5. **Verbosity control**: a `--verbose` / `--debug` flag (or env var) to increase detail.

## Open Questions
- Which command path is authoritative for Ralph in this repo: `tk ralph ...` or `tf new ralph ...` (or both)?
- Where should logs go by default: stdout only, a `.tf/ralph/logs/` file, or both?
- Do we want JSON logs (machine parsing) or keep it plain text for MVP?
- What’s the expected noise budget (how much output is acceptable in normal runs)?
