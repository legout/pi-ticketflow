---
id: pt-v2jv
status: closed
deps: [pt-9zhm]
links: []
created: 2026-02-06T12:37:21Z
type: task
priority: 2
assignee: legout
external-ref: plan-auto-planning-sessions-linkage
tags: [tf, backlog, plan, planning-session]
---
# Implement session-aware /tf-spike auto-linking

## Task
Update the planning spike procedure so `/tf-spike` auto-attaches to the active planning session and writes cross-references in `sources.md`.

## Context
When a session is active, spikes should be recorded under the root seed session and be discoverable without manual linking.

## Acceptance Criteria
- [ ] Creating a spike while a session is active appends the spike id to `spikes[]` in `.active-planning.json` (dedup).
- [ ] Root seed `sources.md` gains a link to the spike `spike.md` in a dedicated “Session Links” section (dedup).
- [ ] Spike `sources.md` gains a link back to the root seed.
- [ ] Emits a one-line notice when auto-attaching.

## Constraints
- Behavior unchanged when no active session exists.

## References
- Plan: plan-auto-planning-sessions-linkage



## Notes

**2026-02-06T13:04:17Z**

## Implementation Complete

Session-aware auto-linking for /tf-spike has been implemented.

### Changes
- Updated Research Spike procedure in skills/tf-planning/SKILL.md
- Added 3 new steps: session detection, session update, cross-linking
- All acceptance criteria met

### Artifacts
- implementation.md - Detailed implementation notes
- review.md - Review findings (0 issues)
- fixes.md - No fixes required
- Commit: 1000399a1adc529c9b09fa06548dabab240f1911

### Verification
To test the changes:
1. Create a planning session: /tf-seed "test session"
2. Run a spike: /tf-spike "test topic"
3. Verify auto-linking in .active-planning.json and sources.md files
