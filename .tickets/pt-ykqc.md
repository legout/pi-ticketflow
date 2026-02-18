---
id: pt-ykqc
status: closed
deps: [pt-9dxh]
links: []
created: 2026-02-17T14:36:52Z
type: task
priority: 2
assignee: legout
external-ref: ralph-loop-parity
tags: [tf, ralph, component:workflow, component:knowledge]
---
# Add lessons extraction and pruning for /ralph-loop

Extract useful lessons from ticket artifacts after completion and append to .tf/ralph/AGENTS.md with pruning according to lessonsMaxCount.

## Acceptance Criteria

Lesson extraction runs after completed tickets; AGENTS.md appended in stable format; pruning enforces max lesson count; no duplicate spam on resume.

