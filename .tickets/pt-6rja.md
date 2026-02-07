---
id: pt-6rja
status: closed
deps: []
links: []
created: 2026-02-06T13:07:53Z
type: task
priority: 2
assignee: legout
external-ref: plan-kb-management-cli
tags: [tf, backlog, plan, knowledge]
---
# Add Python CLI dispatch for tf kb (bypass legacy)

## Task
Route `tf kb ...` through the Python CLI (`tf_cli/cli.py`) so knowledge-base commands do not depend on `scripts/tf_legacy.sh`.

## Context
Currently, many commands fall back to the legacy shell CLI. We need kb management to be Python-native.

## Acceptance Criteria
- [ ] `python -m tf_cli.cli kb --help` works.
- [ ] `tf kb --help` works when running via `bin/tf` shim.
- [ ] No legacy script invocation is required for kb.

## References
- Plan: plan-kb-management-cli



## Notes

**2026-02-06T13:16:03Z**

Implemented Python CLI dispatch for tf kb commands.

Changes:
- Created tf_cli/kb_cli.py with ls, show, index commands
- Added kb dispatch to tf_cli/cli.py
- Fixed review issues: removed unused imports/functions, fixed flag parsing, added JSON support

Commit: eb65f99
Artifacts: .tf/knowledge/tickets/pt-6rja/
