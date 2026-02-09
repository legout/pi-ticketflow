---
id: pt-sf9w
status: open
deps: []
links: [pt-ls9y]
created: 2026-02-09T11:48:25Z
type: task
priority: 2
assignee: legout
external-ref: plan-allow-to-serve-the-textual-app-as-a-web
tags: [tf, backlog, plan, component:cli, component:docs, component:workflow]
---
# Verify Ticketflow UI runs via `textual serve`

## Task
Validate that the Ticketflow Textual UI can be served in a browser using Textual devtools, and record findings for docs.

## Context
Plan requires supporting `textual serve` for both installed and dev workflows.

## Acceptance Criteria
- [ ] Confirm `textual serve "tf ui"` starts and the UI loads in a browser
- [ ] Confirm `textual serve "python -m tf_cli.ui"` works from repo checkout
- [ ] Note defaults (URL/port) and any quirks (shutdown on tab close, latency)

## Constraints
- Keep this as verification + notes; no feature work unless required for basic function

## References
- Plan: plan-allow-to-serve-the-textual-app-as-a-web

