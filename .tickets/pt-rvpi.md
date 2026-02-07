---
id: pt-rvpi
status: closed
deps: [pt-7cri]
links: [pt-ljos, pt-uo6h]
created: 2026-02-06T17:00:29Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-more-logging-to-ralph-loop
tags: [tf, backlog, component:api, component:workflow]
---
# Implement Ralph logger helper (timestamped levels, stderr, redaction)

## Task
Implement a small logging helper for Ralph (level filtering + consistent formatting), and print logs to stderr so stdout can remain workflow output.

## Context
Centralizing logging avoids scattered `print()` calls and makes it easy to tune verbosity and redact sensitive values.

## Acceptance Criteria
- [ ] Helper supports levels (info/warn/error/debug) and includes timestamp.
- [ ] Logs include optional context fields (ticket id, iteration, mode: serial/parallel).
- [ ] Output goes to stderr by default.
- [ ] Redaction helper exists for secrets and overly-large values.

## Constraints
- Must not log full prompts or API keys.

## References
- Seed: seed-add-more-logging-to-ralph-loop


## Notes

**2026-02-06T17:58:39Z**

Implementation complete.

- Created tf_cli/logger.py with RalphLogger, RedactionHelper, LogLevel enum
- Supports levels (debug/info/warn/error) with ISO timestamps
- Context fields: ticket id, iteration, mode (serial/parallel)
- Output to stderr by default
- Redaction for secrets and large values (>1000 chars)
- 41 comprehensive tests added, all 440 tests pass
- Integrated into ralph_new.py replacing print statements
- Fixed critical enum mismatch for VERBOSE/QUIET/NORMAL aliases

Commit: ffd9fdc
