# MVP Scope: seed-automatic-planning-sessions-linkage

## In Scope
- Session state file: `.tf/knowledge/.active-planning.json`
- Session archive snapshots: `.tf/knowledge/sessions/{session_id}.json`
- `/tf-seed`:
  - default activate session
  - `--no-session`
  - archive+switch when active exists
  - `--sessions` listing
  - `--resume` reactivate session
- `/tf-spike`, `/tf-plan`, `/tf-backlog`:
  - detect active session
  - update session state
  - write cross-references into `sources.md` (seed ↔ spike ↔ plan)
  - backlog finalizes (completed snapshot) and deactivates
- Documentation updates in prompts and/or docs

## Out of Scope
- Graph visualization
- Automatic linkage inference without session
- Multi-root sessions (multiple seeds active)
- Automatic migration of old topics into sessions (can be a follow-up)
