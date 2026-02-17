---
id: pt-vajd
status: open
deps: [pt-pdjd, pt-rmix]
links: []
created: 2026-02-17T14:36:52Z
type: task
priority: 2
assignee: legout
external-ref: ralph-loop-parity
tags: [tf, ralph, component:workflow, component:reliability]
---
# Implement retry/restart and escalation controls for /ralph-loop

Add bounded retries for failed/timeouts and optional escalation behavior consistent with Ralph settings and retry-state conventions.

## Acceptance Criteria

Failed tickets retry up to configured limit; timeout retries supported; escalation/max-retry blocking behavior matches project settings; outcomes persisted clearly.

