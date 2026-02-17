---
id: pt-mdl0
status: closed
deps: [pt-74hd]
links: [pt-pcd9, pt-rn2w]
created: 2026-02-13T14:36:13Z
type: task
priority: 2
assignee: legout
external-ref: plan-replace-pi-model-switch-extension
tags: [tf, backlog, plan, component:agents, component:api, component:cli, component:workflow]
---
# Implement /tf as a /chain-prompts wrapper (keep /tf contract)

## Task
Update the `/tf` entry prompt to orchestrate the phase prompts via `/chain-prompts` (or introduce `/tf-irf` and keep `/tf` as alias).

## Context
`pi-prompt-template-model` provides `/chain-prompts templateA -> templateB -- args` with per-step model/skill/thinking. This should replace runtime model switching via `pi-model-switch`.

## Acceptance Criteria
- [ ] `/tf <ticket>` runs `tf-research -> tf-implement -> tf-review -> tf-fix -> tf-close` in order
- [ ] Chain uses shared args correctly (ticket id + flags strategy per design)
- [ ] Original model/thinking restored after chain completes (or fails) per `/chain-prompts` behavior

## References
- Plan: plan-replace-pi-model-switch-extension



## Notes

**2026-02-13T16:04:46Z**

Implemented /tf as chain-prompts wrapper. Added Execution section to .pi/prompts/tf.md with proper chain syntax and fallback sequential execution.

**2026-02-13T17:35:35Z**

Completed deterministic /tf wrapper implementation.

Implemented tf irf CLI backend and wired /tf prompt to delegate to it.

What tf irf does:
- strict flag parsing/validation
- config-aware research entry resolution
- deterministic /chain-prompts command construction
- gated post-chain commands (run only on success)
- --plan/--dry-run support

This preserves /tf contract while removing prompt-level orchestration ambiguity.

Commits: dbd1390, f0cd721
