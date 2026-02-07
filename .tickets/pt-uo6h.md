---
id: pt-uo6h
status: closed
deps: [pt-rvpi]
links: [pt-rvpi]
created: 2026-02-06T17:00:29Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-more-logging-to-ralph-loop
tags: [tf, backlog, component:api, component:cli, component:config, component:workflow]
---
# Implement optional Pi JSON mode capture for deeper debugging (experimental)

## Task
Add an optional debug feature to run Pi with `--mode json` and capture the JSONL stream for a ticket run, so tool execution can be inspected post-mortem.

## Context
Pi can emit an event stream in JSON mode. Capturing this can help debug what happened during non-interactive runs without changing Pi itself.

## Acceptance Criteria
- [ ] A flag/env toggle enables JSON mode capture (default off).
- [ ] JSONL is written to a predictable location (e.g. `.tf/ralph/logs/<ticket>.jsonl`).
- [ ] Log output indicates where the JSONL trace was written.

## Constraints
- Must be opt-in; JSONL may contain file paths or snippets.

## References
- Seed: seed-add-more-logging-to-ralph-loop


## Notes

**2026-02-06T18:23:44Z**

Implementation complete:

- Added --capture-json flag to 'tf ralph run' and 'tf ralph start'
- Added RALPH_CAPTURE_JSON env var support
- Added captureJson config option (default: false)
- JSONL written to .tf/ralph/logs/<ticket>.jsonl
- Log output indicates JSONL location
- 17 new tests added, all 495 tests passing

Priority: CLI flag > env var > config > default
