---
id: pt-7l5c
status: closed
deps: [pt-v2jv]
links: []
created: 2026-02-06T12:37:21Z
type: task
priority: 2
assignee: legout
external-ref: plan-auto-planning-sessions-linkage
tags: [tf, backlog, plan, planning-session]
---
# Implement session-aware /tf-plan attachment + Inputs/Related Topics

## Task
Update `/tf-plan` so when a session is active it attaches the plan to the session and writes an “Inputs / Related Topics” section referencing the root seed + recorded spikes.

## Context
Plans should be self-contained specs with clear provenance (seed + spikes) without manual edits.

## Acceptance Criteria
- [ ] Active session updated with `plan: <plan-id>` (overwriting prior plan for that session).
- [ ] Generated plan includes an “Inputs / Related Topics” section listing root seed and all session spikes.
- [ ] Seed `sources.md` and plan `sources.md` are cross-linked (dedup).
- [ ] Emits a one-line notice when auto-attaching.

## Constraints
- Behavior unchanged when no active session exists.

## References
- Plan: plan-auto-planning-sessions-linkage



## Notes

**2026-02-06T13:06:51Z**

--message ## Implementation Complete

Updated /tf-plan to support session-aware plan attachment:

**Changes:**
- skills/tf-planning/SKILL.md - Added session-aware steps to Plan Interview procedure
- prompts/tf-plan.md - Updated with session behavior documentation

**Features:**
1. Active session detection at start of plan creation
2. "Inputs / Related Topics" section auto-generated when session active
3. Session plan field updated (overwrites prior plan)
4. Cross-linking between seed sources.md and plan sources.md
5. One-line notice emitted on auto-attach

**Commit:** db3abf7
