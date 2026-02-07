---
id: ptw-f3
status: closed
deps: []
links: []
created: 2026-02-05T15:25:00Z
type: task
priority: 3
assignee: legout
external-ref: ptw-6dza
tags: [tf, followup, enhancement]
---
# Enhance keyword detection with scoring system

## Origin
From review of ticket: ptw-6dza
File: skills/tf-planning/SKILL.md (Seed mode hint-based override)

## Issue
The keyword detection logic ("setup", "configure", "define", "design", "implement", "test") could be enhanced with a scoring system for even smarter ordering. For example, a ticket with both "setup" and "configure" keywords gets higher priority than one with just "configure".

## Severity
Suggestion

## Acceptance Criteria
- [ ] Design scoring system for keyword-based ticket ordering
- [ ] Assign weights to keywords (e.g., setup=10, configure=8, define=6, etc.)
- [ ] Implement cumulative scoring for tickets with multiple keywords
- [ ] Document the scoring logic in the skill
- [ ] Add examples showing improved ordering

## Notes

**2026-02-05T16:53:37Z**

--note ## Implementation Complete

Added keyword scoring system to tf-planning skill for smarter ticket ordering during backlog generation.

### Changes Made
- New Step 7: Score and order tickets using keyword weights
- Weights: setup(10), configure(8), define(6), design(5), implement(3), test(1)
- Cumulative scoring for tickets with multiple keywords
- Added comprehensive examples section
- Updated backlog.md format to include Score column

### Review Results
- Critical: 0 | Major: 0 | Minor: 0
- All acceptance criteria satisfied

### Commit
38de3e2 ptw-f3: Add keyword scoring system for smarter ticket ordering
