---
id: ptw-f2
status: closed
deps: []
links: []
created: 2026-02-05T15:25:00Z
type: task
priority: 3
assignee: legout
external-ref: ptw-6dza
tags: [tf, followup]
---
# Standardize tk create command template formatting

## Origin
From review of ticket: ptw-6dza
File: prompts/tf-backlog.md and skills/tf-planning/SKILL.md

## Issue
The `tk create` command templates show `--tags` with varying indentation. Some have 2 spaces before `--tags`, some have none before the backslash. Consider standardizing formatting across all templates for easier parsing/debugging.

## Severity
Warning

## Acceptance Criteria
- [ ] Audit all `tk create` command templates in prompts/tf-backlog.md
- [ ] Audit all `tk create` command templates in skills/tf-planning/SKILL.md
- [ ] Standardize indentation (recommend consistent 2-space or 4-space indentation)
- [ ] Verify no functional changes, only formatting

## Notes

**2026-02-05T16:50:29Z**

## Completed

Standardized all `tk create` command template formatting in skills/tf-planning/SKILL.md.

### Changes Made
- Fixed 6 occurrences of inconsistent --tags indentation (was 3 or 6 spaces, now consistently 2-space continuation indentation)
- Templates affected: Seed, Baseline, Plan, Follow-up, OpenSpec, and Ticket Creation Pattern

### Verification
- prompts/tf-backlog.md already had correct formatting (no changes needed)
- All templates now use consistent 2-space indentation for line continuations

Commit: 86ed4cc
