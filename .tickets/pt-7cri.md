---
id: pt-7cri
status: closed
deps: [pt-l6yb]
links: []
created: 2026-02-06T17:00:29Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-more-logging-to-ralph-loop
tags: [tf, backlog, component:cli, component:config, component:docs, component:workflow]
---
# Configure Ralph verbosity controls (CLI flags + env var)

## Task
Add a minimal mechanism to control Ralph log verbosity (e.g. `--verbose`, `--debug`, and/or `RALPH_LOG_LEVEL`).

## Context
We need a safe default (concise) and an opt-in mode to get more detail during troubleshooting.

## Acceptance Criteria
- [ ] `tf ralph start` and `tf ralph run` accept a verbosity flag (documented in `--help`).
- [ ] An env var override is supported (e.g. `RALPH_LOG_LEVEL=debug`).
- [ ] Verbosity is passed through to the logging helper and used to filter messages.

## Constraints
- No breaking changes to existing invocations (flags optional).

## References
- Seed: seed-add-more-logging-to-ralph-loop


## Notes

**2026-02-06T17:49:24Z**

Implemented verbosity controls for Ralph CLI.

Changes:
- Added --verbose, --debug, --quiet flags to 'tf ralph run' and 'tf ralph start'
- Added env var support: RALPH_LOG_LEVEL, RALPH_VERBOSE, RALPH_DEBUG, RALPH_QUIET
- Added config file support (logLevel in .tf/ralph/config.json)
- Priority: CLI flags > env vars > config > default (normal)
- Verbosity passed through to workflow via flags

Commit: a35343d
Artifacts: .tf/knowledge/tickets/pt-7cri/
