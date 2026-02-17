---
id: pt-pcd9
status: closed
deps: [pt-mdl0]
links: [pt-qmhr, pt-mdl0]
created: 2026-02-13T14:36:13Z
type: task
priority: 2
assignee: legout
external-ref: plan-replace-pi-model-switch-extension
tags: [tf, backlog, plan, component:agents, component:cli, component:config, component:docs, component:workflow]
---
# Update docs/setup to drop pi-model-switch as required extension

## Task
Update documentation and setup scripts to remove `pi-model-switch` from the required extension set when using the `/chain-prompts` workflow.

## Context
Docs currently list `pi-prompt-template-model`, `pi-model-switch`, and `pi-subagents` as required. After refactor, model switching is handled by prompt chaining.

## Acceptance Criteria
- [ ] Docs updated: `docs/architecture.md`, `docs/configuration.md`, and any “Required Extensions” lists
- [ ] Troubleshooting section updated (model switching now via frontmatter + chain)
- [ ] Clear note on rollback/fallback (optional install of `pi-model-switch` if needed)

## References
- Plan: plan-replace-pi-model-switch-extension



## Notes

**2026-02-13T17:35:40Z**

Completed docs/setup migration to drop pi-model-switch as required extension.

Updated setup/doctor/config docs and TF workflow docs:
- required: pi-prompt-template-model, pi-subagents
- optional: pi-review-loop, pi-mcp-adapter, pi-web-access
- removed stale runtime model-switch guidance
- aligned docs with deterministic /tf -> tf irf orchestration

Commits: dbd1390, f0cd721
