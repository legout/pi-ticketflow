---
id: ptw-uv0x
status: closed
deps: []
links: []
created: 2026-02-05T15:01:24Z
type: task
priority: 3
assignee: legout
tags: [tf, followup, enhancement]
---
# Consider adding --links-only flag to tf-backlog

## Origin\nFrom review of: ptw-cn2e\nFile: prompts/tf-backlog.md, skills/tf-planning/SKILL.md\n\n## Issue\nAdd a --links-only flag to run linking on existing backlogs without creating new tickets. This would allow retroactive linking of related tickets in existing backlogs.\n\n## Acceptance Criteria\n- [ ] Add --links-only flag to tf-backlog prompt\n- [ ] Update skill procedure to support links-only mode\n- [ ] Document use case: retroactive linking of existing tickets


## Notes

**2026-02-05T17:12:05Z**

Implemented --links-only flag for /tf-backlog

Changes:
- Updated prompts/tf-backlog.md with --links-only flag, documentation, and examples
- Updated skills/tf-planning/SKILL.md with links-only procedure

The flag enables retroactive linking of existing backlog tickets without creating new ones.

Commit: 6a90663
