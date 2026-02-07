---
id: plan-auto-planning-sessions-linkage
status: approved
last_updated: 2026-02-06
---

# Plan: Automatic planning sessions for seed↔spike↔plan↔backlog linkage

## Summary
Enhance TF planning so seed/spike/plan/backlog artifacts “belong together” automatically.

The core idea is to make `/tf-seed` start (and switch) an **active planning session** rooted at the created seed. While a session is active, `/tf-spike`, `/tf-plan`, and `/tf-backlog` automatically attach themselves to that seed via a small session-state file in `.tf/knowledge/`, and they cross-reference each other in `sources.md`. When `/tf-backlog` completes, the session is marked completed and automatically deactivated.

## Requirements
- `/tf-seed`:
  - Default behavior: create seed artifacts and **activate** a new session.
  - Flag: `--no-session` preserves legacy behavior (no session activation, no archiving).
  - If a session is already active, **archive + switch** to the new seed.
  - Support multiple sessions per seed (timestamped session IDs).
  - Flags:
    - `--sessions [seed-id]` lists archived sessions (optionally filtered).
    - `--resume <seed-id|session-id>` re-activates an archived session (archive+switch semantics apply).
    - `--active` prints the current active session (or “none”).
- `/tf-spike`:
  - If an active session exists, auto-attach the spike id to that session and write cross-references:
    - add spike to root seed `sources.md`
    - add root seed to spike `sources.md`
- `/tf-plan`:
  - If an active session exists, auto-attach the plan id to that session.
  - Plan should include an explicit “Inputs / Related Topics” section referencing the root seed and any recorded spikes.
  - Cross-reference seed↔plan in `sources.md`.
- `/tf-backlog`:
  - If an active session exists, record:
    - topic used for backlog generation
    - created ticket IDs
    - path to `backlog.md`
  - Mark session `completed` and **auto-deactivate** (remove the active pointer file).
- Storage location must respect `workflow.knowledgeDir` (default `.tf/knowledge`).

### UX / CLI output requirements
- When a command auto-attaches to an active session, it should print a single-line notice (stderr or stdout):
  - e.g. `[tf] Active planning session: seed-foo@... (root: seed-foo) — auto-linked spike spike-bar`
- When no active session exists, `/tf-spike` and `/tf-plan` should behave exactly as they do today.

## Constraints
- No new top-level command (prefer enhancing existing `/tf-seed` and session-aware behavior in existing planning commands).
- Backwards compatible: `--no-session` keeps the old behavior.
- No data loss: archiving must be append-only snapshots; do not move topic folders.
- Minimal dependencies: use stdlib JSON; no DB.
- Idempotency: re-running a command should not create duplicate references (in session JSON or in `sources.md`).
- Implementation should work in Pi prompt mode (by updating `skills/tf-planning/SKILL.md` + `prompts/*.md`) without requiring an external service.

## Assumptions
- TF can write new files under `{knowledgeDir}` and create subdirectories as needed.
- `sources.md` exists (or can be created) for seed/spike topics.
- Existing `index.json` readers tolerate extra keys if we add optional metadata.

## Risks & Gaps
- **Ambiguity when resuming by seed-id** (multiple archived sessions):
  - Mitigation: `--resume <seed-id>` resumes “latest for seed”; allow explicit `--resume <session-id>`.
- **Surprise linking** if a user forgets a session is active:
  - Mitigation: auto-deactivate after `/tf-backlog`; emit a clear one-line notice on auto-attach.
- **Partial failures** (e.g., spike created but session update fails):
  - Mitigation: update session state *after* successfully writing topic artifacts; keep operations idempotent.
- **Concurrent runs / race conditions** (two shells both planning):
  - Mitigation (v1): best-effort atomic writes (`write tmp + rename`) for `.active-planning.json` and snapshots. Document that concurrent planning sessions are not supported.
- **sources.md duplication / ordering**:
  - Mitigation: append only if the exact line isn’t present; keep lines in a dedicated “Session Links” section.

## Work Plan (phases / tickets)
1. **Define session data model + storage**
   - Add `{knowledgeDir}/.active-planning.json` (active pointer).
   - Add `{knowledgeDir}/sessions/{session_id}.json` snapshots.
   - Define stable JSON schema (include a `schema_version`).
2. **Implement session operations (helper module/script)**
   - Create/read/update active session.
   - Archive active session (write snapshot, mark state).
   - List sessions (optional filter by seed).
   - Resume session (load snapshot into active pointer).
   - Recommended implementation: a small Python module under `tf_cli/` (so commands can reuse it), plus unit tests.
3. **Enhance `/tf-seed` behavior + flags**
   - Default activate session.
   - Implement `--no-session`, `--sessions`, `--resume`, `--active`.
   - Archive+switch semantics when a session is already active.
   - Update `skills/tf-planning/SKILL.md` “Seed Capture” procedure + `prompts/tf-seed.md` to document flags and session behavior.
4. **Make `/tf-spike` session-aware**
   - Auto-attach spike id to session (dedupe).
   - Cross-reference seed↔spike in `sources.md` (dedupe).
   - Update `skills/tf-planning/SKILL.md` “Research Spike” procedure + `prompts/tf-spike.md` to mention auto-linking when a session is active.
5. **Make `/tf-plan` session-aware**
   - Auto-attach plan id (and keep only one “current plan” per session).
   - Write “Inputs / Related Topics” section (seed + spikes) into the plan.
   - Cross-reference seed↔plan in `sources.md`.
   - Update `skills/tf-planning/SKILL.md` “Plan Interview” procedure + prompt docs accordingly.
6. **Make `/tf-backlog` session-aware**
   - Record ticket IDs + backlog path.
   - Mark session completed and auto-deactivate (remove `.active` pointer).
   - Update `skills/tf-planning/SKILL.md` “Backlog Generation” procedure + `prompts/tf-backlog.md` to document completion + deactivation.
7. **Index/documentation updates**
   - Optionally extend `{knowledgeDir}/index.json` entries with `type`, `root_seed`, `session_id`, `relates` (non-breaking).
   - Update prompt docs (`prompts/tf-seed.md`, and notes in spike/plan/backlog prompts) and `docs/workflows.md`.
8. **Tests**
   - Unit tests for session state transitions + idempotency:
     - seed activates
     - second seed archives prior active
     - spike attaches to active
     - resume by seed-id chooses latest
     - backlog finalizes + deactivates
   - Smoke tests: basic CLI parsing (`tf seed --help` if implemented as subcommand) or prompt-driven behavior where applicable.

## Data Model (concrete)

### Paths (relative to `{knowledgeDir}`)
- Active pointer: `.active-planning.json`
- Archives: `sessions/{session_id}.json`

### Session ID
- Format: `{seed_id}@{UTC timestamp}`
- Timestamp format: `YYYY-MM-DDTHH-MM-SSZ` (filename-safe)

### Active session JSON schema (v1)
```json
{
  "schema_version": 1,
  "session_id": "seed-foo@2026-02-06T17-30-00Z",
  "state": "active",
  "root_seed": "seed-foo",
  "spikes": ["spike-a"],
  "plan": "plan-b",
  "backlog": {
    "topic": "plan-b",
    "backlog_md": "topics/plan-b/backlog.md",
    "tickets": ["ptw-xxxx", "ptw-yyyy"]
  },
  "created": "2026-02-06T17:30:00Z",
  "updated": "2026-02-06T18:10:00Z",
  "completed_at": null
}
```

### Completion + deactivation
- When `/tf-backlog` completes:
  - write a snapshot to `sessions/{session_id}.json` with `state: completed` and `completed_at` set
  - delete `.active-planning.json`

## Acceptance Criteria
- [ ] Running `/tf-seed "..."` creates seed artifacts and sets an active session pointer.
- [ ] Starting a new seed while one is active archives the prior session snapshot and switches.
- [ ] `--no-session` prevents session activation/archiving.
- [ ] `/tf-spike` created during an active session auto-links to the root seed (session state + sources).
- [ ] `/tf-plan` created during an active session references root seed + spikes and updates the session.
- [ ] `/tf-backlog` records created ticket IDs and finalizes the session as completed, then deactivates it.
- [ ] Multiple sessions per seed are supported and resumable via `/tf-seed --resume ...`.
- [ ] Re-running the same commands is safe (no duplicate session entries or duplicate `sources.md` links).

## Open Questions
- Should we also write relationship metadata into `{knowledgeDir}/index.json` entries as part of the MVP, or keep it as a follow-up (session snapshots + sources links are sufficient for v1)?

## Decisions (v1)
- Resume behavior: `/tf-seed --resume ...` **reactivates the same archived session id** (no forking). A future `--fork` can be added later.
- Status output: add `/tf-seed --active` to print the current active session (or “none”).
- Topic cross-linking lives in `sources.md` only (in a dedicated “Session Links” section) for v1; no separate `related.md`.

---

## Consultant Notes (Metis)
- 2026-02-06:
  - Clarified operational UX: commands should emit a one-line “auto-linked” notice when attaching to an active session.
  - Added concrete JSON schema + file paths + session id format to reduce ambiguity.
  - Added explicit idempotency requirements (dedupe both session state and `sources.md`).
  - Identified concurrency/race risk and proposed atomic write mitigation (v1 best-effort).
  - Revision note: resolved key open questions by deciding resume semantics (no fork in v1), adding `--active`, and scoping cross-links to `sources.md`.

## Reviewer Notes (Momus)
- 2026-02-06: FAIL
  - Blockers:
    - None yet (initial draft). Needs review for scope and compatibility.
  - Required changes:
    - (pending)
  - Revision status:
    - Plan revised; ready for re-review.

- 2026-02-06: PASS
  - Notes:
    - Requirements are concrete and testable (flags, archive+switch, auto-deactivate after backlog).
    - Scope boundaries are explicit; no new top-level command requirement is honored.
    - Data model is simple (one active pointer + archived snapshots) and supports multiple sessions per seed.
    - Risks are identified with reasonable mitigations (idempotency, atomic writes).
  - Non-blocking suggestions:
    - Keep `index.json` relationship updates as a follow-up if it complicates MVP; session snapshots + `sources.md` links are sufficient.
    - Implement session JSON read/write in a small shared helper to avoid drift across spike/plan/backlog procedures.
