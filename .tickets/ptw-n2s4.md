---
id: ptw-n2s4
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
# Define version source of truth + sync package metadata

## Task
Decide and document the canonical version source for Ticketflow, and make package metadata consistent with it.

## Context
The seed calls for a single source of truth for the project version. Today, the repo has multiple version fields (e.g., `package.json` vs `pyproject.toml`) that can drift.

## Acceptance Criteria
- [ ] Canonical version source is chosen and documented (file/path + update procedure).
- [ ] `package.json` and `pyproject.toml` (and any other relevant metadata) are updated to match.
- [ ] A short note is added on how to bump versions (manual is fine for MVP).

## Constraints
- Keep it lightweight; no CI/release automation required for MVP.

## References
- Seed: seed-add-versioning


## Notes

**2026-02-05T16:11:53Z**

**Completed: Version Source of Truth**

## Changes
- VERSION file established as canonical version source
- pyproject.toml: dynamic versioning via 
- tf_cli/__init__.py: exposes  for package consumers
- tf_cli/_version.py: reads version at runtime with error handling fallback
- MANIFEST.in: ensures VERSION is included in package distribution
- VERSIONING.md: documents bump procedure and SemVer format

## Verification
-  returns 0.1.0
- Missing VERSION file gracefully falls back to unknown
- All package metadata now consistent at v0.1.0

## Review Summary
- Critical issues fixed: 2 (error handling, MANIFEST.in)
- Minor issues fixed: 1 (documentation)

Commit: 091b732
