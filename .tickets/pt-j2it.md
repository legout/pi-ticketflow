---
id: pt-j2it
status: closed
deps: [pt-m5jv]
links: [pt-l6yb]
created: 2026-02-06T17:00:29Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-more-logging-to-ralph-loop
tags: [tf, backlog, component:api, component:config, component:docs, component:workflow]
---
# Document Ralph logging + troubleshooting (tf ralph start/run)

## Task
Document the new logging behavior and how to enable verbose/debug output when running Ralph.

## Context
Users need to know where logs go, how to increase verbosity, and what artifacts to inspect after failures.

## Acceptance Criteria
- [ ] Docs mention default log output and how to enable verbose/debug.
- [ ] Troubleshooting section includes “where to look” pointers (`.tf/ralph/progress.md`, `.tf/knowledge/tickets/<id>/`).
- [ ] If JSON capture exists, docs include how to use it and where traces are stored.

## Constraints
- Keep docs short and concrete (examples + commands).

## References
- Seed: seed-add-more-logging-to-ralph-loop


## Notes

**2026-02-06T18:18:43Z**

Documentation complete. Updated docs/ralph-logging.md with:

- Clarified logs go to stderr (Quick Start section)
- Added 'Where to look after failures' troubleshooting section covering:
  - Artifact directory structure (.tf/knowledge/tickets/<id>/)
  - File-by-file breakdown of artifact contents
  - Example error log with artifact_path field
  - Quick inspection commands
- Added 'Session traces (experimental)' section documenting JSONL capture

All 478 tests pass. Commit: 2bb648e
