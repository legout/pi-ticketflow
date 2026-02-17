---
id: pt-pdjd
status: open
deps: [pt-rmix]
links: []
created: 2026-02-17T14:36:52Z
type: task
priority: 2
assignee: legout
external-ref: ralph-loop-parity
tags: [tf, ralph, component:workflow, component:reliability]
---
# Add timeout handling for /ralph-loop dispatch sessions

Support per-ticket attempt timeout in /ralph-loop using config values. On timeout, attempt graceful termination before force kill and record termination method.

## Acceptance Criteria

Timeout configured via .tf/ralph/config.json; timed-out session gets graceful terminate then forced kill fallback; status and reason persisted in state/progress.

