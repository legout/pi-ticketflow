---
id: pt-74hd
status: closed
deps: [pt-qmhr]
links: [pt-rn2w, pt-o5ca]
created: 2026-02-13T14:36:13Z
type: task
priority: 2
assignee: legout
external-ref: plan-replace-pi-model-switch-extension
tags: [tf, backlog, plan, component:agents, component:workflow]
---
# Add phase prompts for TF workflow (research/implement/review/fix/close)

## Task
Create phase prompt templates in `.pi/prompts/` for: `tf-research`, `tf-implement`, `tf-review`, `tf-fix`, `tf-close` with explicit `model:`/`thinking:`/`skill:` frontmatter.

## Context
We want `/tf` orchestration via `/chain-prompts`. Only templates with a `model:` field are chainable. Each phase prompt should write the same artifacts as the current monolithic workflow.

## Acceptance Criteria
- [ ] 5 new prompts exist under `.pi/prompts/` with correct frontmatter and descriptions
- [ ] Running each phase prompt directly produces/updates expected artifacts
- [ ] `tf-review` phase still uses `pi-subagents` for parallel reviewer fan-out + merge

## References
- Plan: plan-replace-pi-model-switch-extension



## Notes

**2026-02-13T15:50:51Z**

Implementation complete via /tf workflow.

## Summary
- Created 5 phase prompts with distinct skills: tf-research, tf-implement, tf-review, tf-fix, tf-close
- Each prompt has explicit model:/thinking:/skill: frontmatter for chainable execution
- Fixed 3 Critical issues: retry reset timestamp, parallel review timeout, git commit error handling
- Fixed 5 Major issues: distinct skills, migration path, atomic writes, rollback guidance, post-fix arithmetic
- Fixed 3 Minor issues: deduplication threshold, retry state schema, flag precedence
- Quality gate: PASSED

Commit: 2002afcc55e6562f3c803c42e7740c3e9c6d4b42

**2026-02-13T17:35:30Z**

Completed with project-root asset layout refactor.

Implemented phase prompts and skills for TF workflow:
- prompts/tf-research.md, tf-implement.md, tf-review.md, tf-fix.md, tf-close.md
- skills/tf-research, tf-implement, tf-review-phase, tf-fix, tf-close

Important architecture fix:
- Restored skills/tf-review as reviewer subagent contract
- Added skills/tf-review-phase for phase orchestration
- tf-review prompt now uses skill=tf-review-phase

Note: canonical paths are now project root (prompts/, skills/, agents/) rather than .pi/.

Commits: dbd1390, f0cd721
