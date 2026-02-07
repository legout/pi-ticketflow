---
id: ptw-nw3d
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
# Add version retrieval helper for CLI

## Task
Add a small helper (e.g., `tf_cli/version.py`) that returns the current Ticketflow version reliably.

## Context
`tf --version` should work across install modes (running from repo, pip/uvx install, etc.). Centralizing version lookup prevents duplicated logic.

## Acceptance Criteria
- [ ] A single function (e.g., `get_version() -> str`) exists and is used by CLI entry points.
- [ ] Works when running from a git checkout and when installed as a Python package.
- [ ] Behavior is documented (fallback order, what happens if version can’t be determined).

## Constraints
- Avoid new dependencies unless clearly justified.

## References
- Seed: seed-add-versioning


## Notes

**2026-02-05T16:16:28Z**

## Completed

Created centralized version retrieval helper () that works across all installation modes.

### Changes
- New  with  function
- Updated , , ,  to use centralized module
- Fixed test file imports and mock paths

### Artifacts
- Implementation: 
- Review: 
- Fixes: 

### Verification
0.1.0
0.1.0

Commit: 8e9f440

**2026-02-07T16:01:34Z**

Implementation complete.

**Changes:**
- tf_cli/version.py: Fixed module-level __version__ caching with lazy loading via __getattr__
- tf_cli/version.py: Removed problematic CWD fallback that could return wrong version
- tf_cli/version.py: Clarified docstring comments about fallback order
- tests/test_version.py: Added missing assertion in test_falls_back_to_module_parent

**Commit:** 97cf602

**Review Issues Fixed:**
- Critical: Module-level __version__ caching (1)
- Major: CWD fallback removal, test assertion (2)
- Minor: Comment clarification (1)

**Outstanding:**
- README.md SemVer documentation (requires manual update)
- Warnings/Suggestions tracked for follow-up tickets
