---
id: ptw-ueyl
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
# Implement tf --version (and -V) across entry points

## Task
Implement `tf --version` (and optionally `-V`) to print the current version string.

## Context
Seed success metric: users can reliably retrieve the installed version via CLI. The repo currently has multiple CLI layers (Python + legacy shell) and should behave consistently.

## Acceptance Criteria
- [ ] `tf --version` prints just the version (e.g., `0.1.0`) and exits 0.
- [ ] `tf -V` works (if implemented) and is documented in usage/help output.
- [ ] No breaking changes to existing command behavior.

## Constraints
- Additive only; keep implementation simple.

## References
- Seed: seed-add-versioning

## Notes

**2026-02-05T16:33:43Z**

Implemented tf --version, -v, and -V flags across all entry points.

Changes:
- tf_cli/cli.py: Added -V flag support alongside --version and -v
- scripts/tf_legacy.sh: Added version flag support with proper newline handling
- tests/test_cli_version.py: Added test for -V flag

All 9 tests pass. Commit: 6258afe

**2026-02-07T16:30:55Z**

Implemented and documented tf --version, -v, -V flags.

Changes:
- Updated help text in tf_cli/cli.py to document version flags

All acceptance criteria met:
- tf --version prints version and exits 0
- tf -V works and is documented
- No breaking changes

Tests: 128 version-related tests pass.
Commit: 0cd4169
