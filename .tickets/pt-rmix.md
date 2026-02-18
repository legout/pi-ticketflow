---
id: pt-rmix
status: closed
deps: [pt-9hgu]
links: []
created: 2026-02-17T14:36:52Z
type: task
priority: 2
assignee: legout
external-ref: ralph-loop-parity
tags: [tf, ralph, component:workflow]
---
# Implement robust completion handling in /ralph-loop (promise sigil + exit state)

Handle dispatch completion events robustly. Prefer lifecycle completion, parse promise sigils from output for diagnostics, and classify outcomes consistently.

## Acceptance Criteria

Completion detected from dispatch/session lifecycle; promise sigils parsed when present; success/failure classification written to run state; unknown states handled conservatively.

