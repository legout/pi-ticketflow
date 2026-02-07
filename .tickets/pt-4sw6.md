---
id: pt-4sw6
status: closed
deps: [pt-gmpy]
links: [pt-gmpy]
created: 2026-02-07T14:23:31Z
type: task
priority: 2
assignee: legout
external-ref: seed-when-executing-tf-backlog-in-an-active-s
tags: [tf, backlog, component:docs, component:tests, component:workflow]
---
# Test /tf-backlog session-aware defaulting and inputs

## Task
Add tests to cover /tf-backlog behavior when an active planning session exists, including default topic selection and inclusion of plan/spike docs.

## Context
Session lifecycle and storage are already tested in tests/test_session_store.py. We need coverage that /tf-backlog resolves topic correctly and reports which inputs were used.

## Acceptance Criteria
- [ ] Unit tests for “no-arg backlog uses root_seed when session active”
- [ ] Unit tests for override behavior when explicit topic arg is provided
- [ ] Unit tests for including plan/spike docs (or at least the input-resolution layer)

## Constraints
- Tests should not call real tk or require network access

## References
- Seed: seed-when-executing-tf-backlog-in-an-active-s



## Notes

**2026-02-07T16:33:10Z**

--note Implementation complete. Added 18 unit tests in tests/test_backlog_session_aware.py covering session-aware topic resolution, input incorporation (plan/spike docs), notifications, and state validation. All acceptance criteria met. Commit: 5568421
