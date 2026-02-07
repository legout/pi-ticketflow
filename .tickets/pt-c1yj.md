---
id: pt-c1yj
status: closed
deps: []
links: [pt-m2qh]
created: 2026-02-07T14:23:31Z
type: task
priority: 2
assignee: legout
external-ref: seed-when-executing-tf-backlog-in-an-active-s
tags: [tf, backlog, component:cli, component:docs, component:workflow]
---
# Define /tf-backlog session-default topic rules and UX

## Task
Define the intended behavior for /tf-backlog when a planning session is active, including default topic selection and user-facing notices.

## Context
Users start a planning session with /tf-seed, then expect /tf-backlog to use that session context automatically. Today, /tf-backlog requires an explicit topic-id/path, which is redundant and error-prone.

## Acceptance Criteria
- [ ] Document rule: if no arg is provided and an active session exists, use session.root_seed as the backlog topic
- [ ] Document override rule: explicit topic arg takes precedence over session
- [ ] Document which session inputs are consulted (plan + spikes) and how they’re reported in output

## Constraints
- Backward compatible for explicit-argument usage
- Avoid surprising implicit behavior; always print a short notice when session is used

## References
- Seed: seed-when-executing-tf-backlog-in-an-active-s



## Notes

**2026-02-07T14:28:28Z**

## Completed

Documented /tf-backlog session-default topic rules and UX.

### Changes Made
- Updated prompts/tf-backlog.md with session-aware behavior documentation
- Added Argument Precedence section (default topic from session, explicit override)
- Added Session Inputs section documenting what gets consulted (root_seed, plan, spikes)
- Added Session Notice Format section with exact UX output format
- Updated Usage section to show argument is optional when session is active
- Added Session Default Example showing the flow

### Acceptance Criteria
- [x] Document rule: if no arg provided and active session exists, use session.root_seed
- [x] Document override rule: explicit topic arg takes precedence over session  
- [x] Document which session inputs are consulted (plan + spikes) and reporting format

### Artifacts
- Commit: 607973a5055a
- Review: 0 issues (documentation change)

Closes ticket.
