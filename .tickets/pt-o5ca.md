---
id: pt-o5ca
status: closed
deps: []
links: [pt-74hd]
created: 2026-02-13T14:36:13Z
type: task
priority: 2
assignee: legout
external-ref: plan-replace-pi-model-switch-extension
tags: [tf, backlog, plan, component:cli, component:docs, component:workflow]
---
# Decide flag strategy for chain-prompts TF workflow

## Task
Decide and document how `/tf` flags map to a `/chain-prompts`-based workflow (e.g., multiple entry prompts vs. conditional logic inside phase prompts).

## Context
The `/chain-prompts` feature is purely sequential and has no branching. TF currently supports flags like `--no-research`, `--with-research`, and optional follow-up steps.

## Acceptance Criteria
- [ ] Chosen approach documented (including rationale and examples)
- [ ] Concrete mapping for: `--no-research`, `--with-research`, `--create-followups`, `--final-review-loop`, `--simplify-tickets`
- [ ] Backward compatibility story for `/tf <id>` clarified

## References
- Plan: plan-replace-pi-model-switch-extension



## Notes

**2026-02-13T15:21:11Z**

--note Completed flag strategy decision for chain-prompts TF workflow.

**Decision**: Hybrid approach
- Research control: Entry point variants (/tf-research, /tf-implement)
- Post-chain steps: Separate commands after chain completes
- Backward compatibility: /tf <id> preserved as wrapper

**Key mappings documented**:
- --no-research → skip research phase
- --create-followups → post-chain /tf-followups
- --final-review-loop → post-chain /review-start
- --simplify-tickets → post-chain /simplify

See implementation.md and close-summary.md for full details.

Unblocks: pt-74hd (phase prompts), pt-mdl0 (wrapper implementation)
Blocked by: pt-qmhr (retry/escalation design)

**2026-02-13T15:23:59Z**

Decision: Hybrid flag strategy - entry points for research control + post-chain commands. Fixed Major(2), Minor(1). Quality Gate PASSED. Commit: 2324ce4

**2026-02-13T16:32:46Z**

Completed flag strategy decision for chain-prompts TF workflow.

**Decision**: Hybrid approach combining entry point variants for research control with post-chain commands for optional follow-up steps.

**Key mappings documented**:
- --no-research → skip research phase (entry point: tf-implement)
- --with-research → force research phase (entry point: tf-research)
- --create-followups → post-chain /tf-followups
- --final-review-loop → post-chain /review-start
- --simplify-tickets → post-chain /simplify

**Quality Gate**: PASSED
- Pre-fix: Critical(4), Major(5), Minor(3)
- Post-fix: Critical(0), Major(0), Minor(0)

Commit: 5e3b5ea

Unblocks: pt-74hd (phase prompts implementation)
Blocked by: pt-qmhr (retry/escalation design)

**2026-02-13T16:56:49Z**

Updated: Created project-level phase skills and prompts architecture.

**Architecture**:
- Skills in `skills/` contain detailed procedures
- Prompts in `prompts/` are thin wrappers with frontmatter
- Keep existing agents in `agents/` for parallel reviews

**Files created**:
- skills/tf-research/SKILL.md, tf-implement, tf-review, tf-fix, tf-close
- prompts/tf-research.md, tf-implement.md, tf-review.md, tf-fix.md, tf-close.md

**Updated**:
- prompts/tf.md - chain invocation with /chain-prompts
- skills/tf-workflow/SKILL.md - orchestration focus
- Plan and spike documents

Commits: 46372e9, 7c4beb8
