---
id: pt-f9cy
status: closed
deps: [pt-9hgu]
links: []
created: 2026-02-17T14:36:52Z
type: task
priority: 2
assignee: legout
external-ref: ralph-loop-parity
tags: [tf, ralph, component:workflow, component:scheduling]
---
# Harden parallel component-safety selection in /ralph-loop

Implement deterministic component conflict filtering using ticket component tags, including untagged ticket policy and active-session overlap checks.

## Acceptance Criteria

Parallel launch never starts conflicting component tickets together; untagged policy is explicit; selection logic is deterministic and tested with sample tickets.

