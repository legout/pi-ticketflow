---
id: ptw-f1
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
# Document --no-deps flag in procedure introduction

## Origin
From review of ticket: ptw-6dza
File: skills/tf-planning/SKILL.md
Section: Procedure introduction

## Issue
The `--no-deps` flag is only mentioned in step 9 (dependency inference). Consider adding documentation in the procedure introduction or a note in step 1 (detect mode) that the flag affects behavior, ensuring implementers are aware of the option early in the process.

## Severity
Warning

## Acceptance Criteria
- [ ] Add note about `--no-deps` flag in the Backlog Generation procedure introduction
- [ ] Mention flag in step 1 (detect mode) or early in the procedure
- [ ] Ensure implementers are aware of the option before they start creating tickets

## Notes

**2026-02-05T16:48:38Z**

## Implementation Complete

Added documentation for the &#96;--no-deps&#96; flag in the Backlog Generation procedure:

1. **Added Flags section** in procedure introduction documenting the &#96;--no-deps&#96; option
2. **Updated Step 2 (detect mode)** with a note referencing the flag and pointing to step 9

All acceptance criteria met:
- [x] Flag documented in procedure introduction
- [x] Flag mentioned early in procedure (step 2)
- [x] Implementers aware of option before creating tickets

Commit: 291b99a
