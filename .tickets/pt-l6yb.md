---
id: pt-l6yb
status: closed
deps: []
links: [pt-j2it]
created: 2026-02-06T17:00:28Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-more-logging-to-ralph-loop
tags: [tf, backlog, component:api, component:workflow]
---
# Define Ralph logging spec (events, fields, redaction)

## Task
Define what Ralph should log (and not log) in normal vs verbose mode, including a stable log line format and redaction rules.

## Context
Ralph currently prints a few status lines, but failures are hard to diagnose. A small logging spec will keep implementation consistent and avoid leaking secrets.

## Acceptance Criteria
- [ ] Log format is defined (timestamp, level, iteration, ticket id, phase/event).
- [ ] Key lifecycle events are enumerated (loop start/end, iteration start/end, selection decisions, phase transitions, errors).
- [ ] Redaction rules are defined (no API keys/tokens; limit tool args shown).

## Constraints
- Default output must remain readable (avoid spam).

## References
- Seed: seed-add-more-logging-to-ralph-loop


## Notes

**2026-02-06T17:41:56Z**

Implemented Ralph logging spec:

- Created comprehensive logging specification (.tf/knowledge/tickets/pt-l6yb/ralph-logging-spec.md)
- Defines log format: TIMESTAMP [LEVEL] [iteration:N] [ticket:ID] [phase:PHASE] message
- Enumerates 18 lifecycle events (loop/iteration/ticket/phase/command/subagent)
- Establishes redaction rules for secrets (API keys, tokens, passwords, URL credentials, SSH keys)
- Defines 3 verbosity modes: quiet, normal, verbose
- Created user-facing docs (docs/ralph-logging.md)

All acceptance criteria met. Commit: 6b298e6
