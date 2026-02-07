---
id: plan-simple-kanban-ui-for-tf
status: approved
last_updated: 2026-02-05
---

# Plan: Simple Kanban UI for Ticketflow (.tf)

## Summary
Provide a lightweight UI (terminal-first, with an optional future web mode) to monitor the current ticket queue in a Kanban-style board and quickly open related artifacts stored under `.tf/` (knowledge base, ticket artifacts, topics, Ralph state).

The UI should be **read-only by default** and optimized for “what should I work on next?”: show status columns, basic metadata, fast search/filtering, and one-keystroke navigation into the underlying markdown documents.

## Requirements
- Kanban-style view of “current tickets”, grouped by status columns.
- Manual refresh keybinding; optional auto-refresh (poll) with a configurable interval.
- Ticket details panel for the selected ticket (id, title, status, tags, priority, updated/created time if available).
- Read-only navigation actions:
  - Open ticket file in `$PAGER`/`$EDITOR`.
  - Open associated `.tf/knowledge/tickets/<id>/` folder when present.
  - Open `.tf/knowledge/topics/*` plan/seed/spike docs.
- “Documents browser” for `.tf/`:
  - Browse `.tf/knowledge/` (topics, ticket artifacts).
  - Browse `.tf/ralph/` (status, lessons, worktrees) when present.
  - View markdown content inline (basic) and/or open externally.
- Works with both:
  - Global installs (`tf ...`)
  - Project installs (`./.tf/bin/tf ...`)
- No network required.

### Concrete v1 ticket source decision (resolves prior blocker)
- **Primary source of truth (v1):** the on-disk ticket store at `./.tickets/*.md` (as created/managed by `tk`).
- **Provider fallback (v1):** if `.tickets/` is missing/empty, display an explicit error with guidance (install/configure `tk`, or run in a repo with `.tickets`).
- **Optional follow-up:** add a `tk`-CLI provider *only if* `tk` offers a stable machine-readable output (e.g. `tk list --json`).

### Status → Kanban column mapping (v1)
- The UI will support a default ordered set of columns and place unknown statuses into “Other”:
  1. Ready
  2. In Progress
  3. Review
  4. Fix
  5. Blocked
  6. Closed
  7. Other
- Mapping rule (configurable): map raw `status:` values from ticket frontmatter into these columns.
  - Example default mapping (to be refined once we confirm real status vocabulary):
    - `ready`, `open` → Ready
    - `in_progress`, `doing` → In Progress
    - `review` → Review
    - `fix`, `fixing` → Fix
    - `blocked` → Blocked
    - `closed`, `done` → Closed

### Non-Goals (v1)
- Editing tickets (changing status, adding notes, linking/deps) from the UI.
- A multi-user/shared web dashboard.
- Perfect markdown rendering (plain text preview is fine).
- Live push updates; polling/manual refresh is sufficient.

## Constraints
- Must run locally and be simple to install via PyPI; keep dependencies minimal.
- Should degrade gracefully when expected directories are missing (`.tf/knowledge`, `.tf/ralph`, `.tf/knowledge/tickets/<id>`).
- Should not mutate tickets/knowledge files unless we explicitly add “edit” features later.
- Cross-platform behavior (Linux/macOS; Windows best-effort) for opening files.
- Prefer stdlib-only parsing for ticket frontmatter (avoid pulling in a full YAML dependency for v1).
- Prefer shipping the TUI dependency as an optional extra (e.g. `pi-tk-workflow[ui]`) so core CLI installs stay lightweight.

## Assumptions
- Ticket files in `.tickets/*.md` have a predictable “YAML frontmatter-like” header:
  - Starts with `---` and ends with `---`
  - Contains simple `key: value` pairs and list values like `[a, b]` (no nested structures required for v1)
- The `.tf/knowledge/` layout follows the documented structure (topics/, tickets/).
- Users will accept a TUI as the initial version.

## Risks & Gaps
- **Status vocabulary mismatch:** the set of real `status:` values used by `tk` may differ from the assumed mapping.
  - Mitigation: make mapping configurable; add an “Other” column; show raw status in details.
- **Frontmatter parsing edge cases:** tickets might include more complex YAML than anticipated.
  - Mitigation: implement a conservative parser for the subset we need; if parsing fails, show ticket as “Unreadable” with error details and allow opening the raw file.
- **Dependency weight:** adding a TUI framework (e.g. Textual) increases install size.
  - Mitigation: ship UI as an optional extra (`pip install pi-tk-workflow[ui]`) or keep the UI framework lightweight.
- **Markdown rendering complexity:** good markdown rendering in a TUI can balloon scope.
  - Mitigation: v1 uses plain text + minimal formatting; external open remains first-class.

## Work Plan (phases / tickets)
1. **Discovery & contracts**
   - Confirm ticket file format contract from real `.tickets/*.md` samples (fields present, status values).
   - Define a minimal internal `Ticket` model:
     - `id`, `title`, `status_raw`, `status_column`, `tags`, `priority`, `created`, `path`
   - Define a `TicketProvider` interface with a v1 implementation reading `.tickets/`.
2. **CLI entry point**
   - Add `tf ui` (alias: `tf dashboard` if desired).
   - Options (v1):
     - `--tickets-dir` (default: `./.tickets`)
     - `--tf-dir` (default: `./.tf`)
     - `--refresh <seconds>` (optional)
3. **Implement TUI skeleton (v1 scope)**
   - Choose framework:
     - Preferred: `textual` for layout/widgets
     - Alternative: `rich` + minimal input handling
   - Layout:
     - Kanban columns (scrollable)
     - Details pane
     - Footer with keybindings
   - Implement: refresh, selection movement, open-in-editor/pager.
4. **Documents browser (v1)**
   - Add a screen/panel to browse `.tf/knowledge` and `.tf/ralph` directories.
   - Inline preview for markdown as plain text; open external remains primary.
5. **Polish & UX (v1)**
   - Search/filter by substring (id/title/tag).
   - Empty states and actionable error messages.
   - Configurable status mapping (simple JSON in `.tf/config/settings.json` or a small `ui.json`).
6. **Testing & packaging**
   - Unit tests for:
     - ticket discovery in `.tickets/`
     - frontmatter parsing (happy path + broken files)
     - status mapping
     - path resolution to `.tf/knowledge/tickets/<id>/`
   - Smoke test: `tf ui --help`.
   - README section: “UI / Dashboard”.
7. **Optional follow-up: Web UI**
   - Only if the TUI is insufficient.
   - Reuse the same `TicketProvider` + `DocumentProvider`.

## Acceptance Criteria
- [ ] `tf ui` opens a TUI that displays tickets from `./.tickets/*.md` grouped into status columns.
- [ ] Selecting a ticket shows details including raw status and file path.
- [ ] A keybinding opens the selected ticket in `$PAGER` or `$EDITOR`.
- [ ] A docs browser can navigate `.tf/knowledge/` and `.tf/ralph/` (when present) and open files.
- [ ] Missing `.tf/knowledge` / `.tf/ralph` / `.tf/knowledge/tickets/<id>` does not crash the UI.
- [ ] If tickets cannot be parsed, the UI shows a clear error and still allows opening the raw ticket file.
- [ ] Packaging supports an optional UI extra (e.g. `pip install pi-tk-workflow[ui]`) and `tf ui --help` works when installed.

## Open Questions
- What are the exact `status:` values produced/expected by `tk` in real usage (ready/open/in_progress/review/fix/blocked/closed)?
- Do we want v1 to support *any* write actions (e.g., “open ticket file in editor” is fine; changing status is out-of-scope)?
- Should docs browsing include non-`.tf/` files (README, etc.), or stay `.tf`-only?

---

## Consultant Notes (Metis)
- 2026-02-05:
  - Resolved the main blocker by making a concrete v1 decision: read tickets directly from `./.tickets/*.md` (on-disk store) rather than depending on `tk` output.
  - Added an explicit (configurable) status→column mapping with an “Other” bucket.
  - Tightened constraints to prefer stdlib-only frontmatter parsing for v1 to avoid a YAML dependency.
  - Scoped markdown rendering to “minimal/plain text” to avoid UI over-engineering.
  - Revision note: added explicit v1 non-goals to prevent scope creep (no ticket editing, no web dashboard, no full markdown rendering).

## Reviewer Notes (Momus)
- 2026-02-05: FAIL
  - Blockers:
    - Ticket source-of-truth is not specified; Kanban columns depend on it.
  - Required changes:
    - Add a concrete decision for v1: which command/file is used to list tickets + statuses, and how statuses map to columns.
  - Revision status:
    - Addressed in this revision (see “Concrete v1 ticket source decision” and “Status → Kanban column mapping”). Re-review requested.

- 2026-02-05: PASS
  - Notes:
    - Scope boundaries are clear (explicit v1 non-goals).
    - Work plan is sequenced and feasible; key early risks (status mapping, parsing) have mitigations.
  - Suggestions (non-blocking):
    - Prefer a two-layer architecture: `TicketProvider` (data) + `UiApp` (presentation) so a future web UI can reuse the same provider.
    - Start with polling/manual refresh; add file watching only after real user demand.
