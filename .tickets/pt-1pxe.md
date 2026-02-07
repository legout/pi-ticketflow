---
id: pt-1pxe
status: closed
deps: [pt-fsk3]
links: []
created: 2026-02-06T13:07:53Z
type: task
priority: 2
assignee: legout
external-ref: plan-kb-management-cli
tags: [tf, backlog, plan, knowledge]
---
# Implement tf kb ls + show

## Task
Implement `tf kb ls` and `tf kb show <topic-id>`.

## Acceptance Criteria
- [ ] `ls` lists active topics from index.json with basic fields.
- [ ] `ls --type seed|plan|spike|baseline` filters by id prefix.
- [ ] `ls --archived` includes archived topics by scanning `.tf/knowledge/archive/topics/`.
- [ ] `show` prints topic metadata and key doc paths and indicates archived status.

## References
- Plan: plan-kb-management-cli



## Notes

**2026-02-06T13:23:49Z**

Implemented tf kb ls and tf kb show commands.

Features:
- ls: Lists active topics from index.json with type and title
- ls --type: Filters by topic type (seed, plan, spike, baseline)
- ls --archived: Includes archived topics from archive directory
- show: Displays topic metadata, keywords, and document existence
- Both commands support --json output

Files changed:
- tf_cli/kb_cli.py
- tf_cli/kb_helpers.py
- tests/test_kb_helpers.py

All 281 tests pass.
