---
id: pt-qdp1
status: closed
deps: [pt-jpyf]
links: []
created: 2026-02-06T12:37:21Z
type: task
priority: 2
assignee: legout
external-ref: plan-auto-planning-sessions-linkage
tags: [tf, backlog, plan, planning-session]
---
# Update prompts/docs to document planning sessions

## Task
Update prompt docs and workflow docs to document the new session behavior and flags.

## Context
Session behavior must be discoverable: `/tf-seed` activates by default; other commands auto-link when active; backlog completion deactivates.

## Acceptance Criteria
- [ ] `prompts/tf-seed.md` documents `--no-session`, `--active`, `--sessions`, `--resume`.
- [ ] `prompts/tf-spike.md`, `prompts/tf-plan.md`, `prompts/tf-backlog.md` mention auto-linking when a session is active.
- [ ] `docs/workflows.md` includes a short “Planning Sessions” note.

## Constraints
- Keep docs concise and aligned with actual behavior.

## References
- Plan: plan-auto-planning-sessions-linkage



## Notes

**2026-02-06T13:45:08Z**

Documentation updated to document planning session behavior:

- prompts/tf-spike.md: Added Session Behavior section documenting auto-linking
- prompts/tf-backlog.md: Added Session Behavior section documenting session finalization
- docs/workflows.md: Added comprehensive Planning Sessions section

Commit: f6d6cec

Acceptance criteria:
✅ prompts/tf-seed.md documents session flags (already existed)
✅ prompts/tf-spike.md mentions auto-linking when session active
✅ prompts/tf-plan.md mentions auto-linking when session active (already existed)
✅ prompts/tf-backlog.md mentions auto-linking and session deactivation
✅ docs/workflows.md includes Planning Sessions section
