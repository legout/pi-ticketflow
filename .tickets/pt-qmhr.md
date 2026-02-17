---
id: pt-qmhr
status: closed
deps: [pt-o5ca]
links: [pt-pcd9]
created: 2026-02-13T14:36:13Z
type: task
priority: 2
assignee: legout
external-ref: plan-replace-pi-model-switch-extension
tags: [tf, backlog, plan, component:agents, component:api, component:config, component:docs, component:workflow]
---
# Design retry/escalation handling for chained TF phases

## Task
Define how retry state and (optional) escalation will work when `/tf` is implemented as a prompt chain (no runtime `switch_model`).

## Context
Current `tf-workflow` describes retry-state persisted in `.tf/knowledge/tickets/<id>/retry-state.json` and optional model escalation. With prompt chaining, each phase runs as a separate prompt step with its own model frontmatter.

## Acceptance Criteria
- [ ] Decide whether escalation is removed, kept, or re-scoped (and where logic lives)
- [ ] Define which artifact(s) represent retry status and what blocks closing
- [ ] Document expected behavior on mid-chain failure (stop vs continue)

## References
- Plan: plan-replace-pi-model-switch-extension



## Notes

**2026-02-13T15:32:01Z**

Design complete for retry/escalation handling in chained TF phases. Key decision: Keep retry logic centralized in orchestrator (/tf prompt) while delegating phase execution to subagents. This preserves existing retry behavior while enabling prompt chain migration. Addressed major issues from review: flag handling completeness, state file concurrency, mid-chain resume detection, and schema additions. Commit: 03a4935

**2026-02-13T17:40:32Z**

Analyzed remaining open /tf-refactor tickets. This was the only open ticket still tied to external-ref=plan-replace-pi-model-switch-extension.

Status assessment:
- Retry/escalation design already documented (note + prior commit 03a4935)
- Deterministic orchestration now implemented via tf irf (dbd1390)
- /tf wrapper + docs now aligned with chain-prompts and failure gating semantics (dbd1390, f0cd721)
- No additional open tickets remain under this /tf refactor plan.

Closing as completed under current architecture.
