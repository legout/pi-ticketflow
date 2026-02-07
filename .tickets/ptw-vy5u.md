---
id: ptw-vy5u
status: closed
deps: []
links: []
created: 2026-02-05T13:38:19Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-versioning
tags: [tf, backlog]
---
# Document versioning + release steps in README/docs

## Task
Document the versioning scheme and the human release process (bump → changelog → tag) in README and/or docs.

## Context
Seed calls for SemVer and predictable releases; the workflow should be easy for maintainers to follow.

## Acceptance Criteria
- [ ] SemVer policy documented (what triggers major/minor/patch).
- [ ] Release checklist documented (update version, update changelog, create git tag).
- [ ] Document where the canonical version lives.

## Constraints
- Keep documentation short and actionable.

## References
- Seed: seed-add-versioning


## Notes

**2026-02-05T16:38:50Z**

Completed: Documented versioning scheme and release process.

Changes:
- Rewrote VERSIONING.md with SemVer policy table, decision matrix, and 7-step release checklist
- Added 'Versioning and Releases' section to README.md with quick reference

Commit: 17e5ddd
Review: 0 Critical / 0 Major / 0 Minor / 1 Suggestion (helper script idea)

**2026-02-07T16:36:52Z**

Completed: Documented versioning scheme and release process in VERSIONING.md and README.md.

Changes:
- VERSIONING.md: SemVer policy with decision matrix, 7-step release checklist, canonical version source
- README.md: Versioning section with quick reference

Commit: 17e5ddd
Review: 0 Critical, 0 Major, 0 Minor issues
