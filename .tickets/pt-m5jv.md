---
id: pt-m5jv
status: closed
deps: [pt-2sea]
links: []
created: 2026-02-06T17:00:29Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-more-logging-to-ralph-loop
tags: [tf, backlog, component:tests, component:workflow]
---
# Test Ralph logging (serial + parallel selection) with captured stderr

## Task
Add tests that validate the new logging helper formatting and key lifecycle logs (without executing real `pi`).

## Context
We want confidence that logs stay stable and that redaction works. Tests should not require network or real ticket execution.

## Acceptance Criteria
- [ ] Unit tests cover logger formatting + level filtering + redaction.
- [ ] Tests simulate serial loop decision logging (no ready tickets / selected ticket).
- [ ] Tests do not invoke real `pi` or modify `.tickets/`.

## Constraints
- Use temp dirs / monkeypatch for filesystem + subprocess stubs.

## References
- Seed: seed-add-more-logging-to-ralph-loop


## Notes

**2026-02-06T18:16:48Z**

Implementation complete. Added 38 tests covering Ralph logging lifecycle events (serial + parallel selection). All tests pass. Commit: 6ffbba8
