---
id: ptw-v5tg
status: closed
deps: []
links: []
created: 2026-02-05T13:38:20Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-versioning
tags: [tf, backlog]
---
# Add minimal smoke test for tf --version

## Task
Add a minimal smoke test to ensure `tf --version` returns a version string and exits successfully.

## Context
Version output should not regress silently; a small test helps catch breakage early.

## Acceptance Criteria
- [ ] A test (or script) runs `tf --version` and asserts exit code 0.
- [ ] Output is non-empty and matches expected format (basic SemVer check).
- [ ] Document how to run the test locally.

## Constraints
- Prefer stdlib-only (no new test framework required for MVP).

## References
- Seed: seed-add-versioning

## Notes

**2026-02-05T16:35:35Z**

Implemented minimal smoke test for tf --version

Changes:
- Added tests/smoke_test_version.py (stdlib-only, no pytest required)
- Validates exit code 0, non-empty output, and SemVer format
- Added Development section to README with test instructions

Tested: python tests/smoke_test_version.py (all checks pass)
Commit: 40723f5
