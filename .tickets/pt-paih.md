---
id: pt-paih
status: closed
deps: [pt-74c7]
links: []
created: 2026-02-06T13:07:53Z
type: task
priority: 2
assignee: legout
external-ref: plan-kb-management-cli
tags: [tf, backlog, plan, knowledge]
---
# Implement tf kb delete (permanent) + index cleanup

## Task
Implement `tf kb delete <topic-id>` as **permanent deletion** for active or archived topics and remove any index.json entry.

## Acceptance Criteria
- [ ] Deleting an active topic removes `.tf/knowledge/topics/<id>`.
- [ ] Deleting an archived topic removes `.tf/knowledge/archive/topics/<id>`.
- [ ] Index entry (if any) is removed.
- [ ] Command prints the deleted path(s) and exits non-zero if topic not found.

## Constraints
- Permanent deletion requested.

## References
- Plan: plan-kb-management-cli



## Notes

**2026-02-06T13:33:00Z**

Implemented tf kb delete <topic-id> command

Changes:
- Added cmd_delete() function to kb_cli.py
- Deletes topics from active (topics/) and archive (archive/topics/) locations
- Removes entry from index.json
- Returns exit code 1 if topic not found
- Updated usage documentation

Testing:
- Syntax check passed
- All 33 existing kb_helpers tests passed
- Manual testing verified delete for active and archived topics
- Error handling verified

Commit: f1fbc5c
