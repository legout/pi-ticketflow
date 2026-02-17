---
id: pt-lbvu
status: closed
deps: [pt-7lrp]
links: [pt-7lrp, pt-9uxj]
created: 2026-02-10T12:39:47Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-retry-logic-on-failed-tickets
tags: [tf, backlog, component:agents, component:config, component:docs, component:tests, component:workflow]
---
# Add escalation config to settings (workflow.escalation)

## Task
Extend settings schema to support retry escalation (enabled/maxRetries/model overrides per role).

## Context
On retries we want to switch fixer/review (and optionally worker) to more capable models like `openai-codex/gpt-5.3-codex` to improve convergence.
This backlog is derived from an approved plan (plan-retry-logic-quality-gate-blocked, status=approved).

## Acceptance Criteria
- [ ] `workflow.escalation` config is added with explicit defaults (enabled=false, maxRetries=3, models nullable).
- [ ] Documented how model overrides map to roles (fixer, reviewer-second-opinion, worker).
- [ ] Backwards compatible when escalation disabled.

## Constraints
- Config must be versionable in repo settings.

## References
- Seed: seed-add-retry-logic-on-failed-tickets
- Plan: plan-retry-logic-quality-gate-blocked


## Notes

**2026-02-10T13:32:03Z**

Implementation verified and reviewed. Escalation config already exists in settings.json with explicit defaults (enabled=false, maxRetries=3, nullable models). Documentation complete in docs/retries-and-escalation.md. All acceptance criteria met. Commit: b209f219

**2026-02-10T13:34:59Z**

Implementation complete.

Added escalation config to settings schema with explicit defaults:
- enabled: false (backwards compatible)
- maxRetries: 3
- models: {fixer: null, reviewerSecondOpinion: null, worker: null}

Updated docs/configuration.md with comprehensive escalation documentation including configuration table, escalation curve, and usage example.

Fixed Major review issue: IOError in load_escalation_config() now logs warning instead of silently swallowing.

All 60 tests passing. Commit: e85c201

**2026-02-10T13:35:40Z**

Implementation complete.

Escalation config was already present in settings.json with correct schema:
- enabled: false (backwards compatible)
- maxRetries: 3
- models: {fixer, reviewerSecondOpinion, worker} all nullable

Fixed 1 Major issue in tf/retry_state.py:
- load_escalation_config() now distinguishes PermissionError from IOError
- Permission errors logged at ERROR level for visibility

Documentation exists at docs/retries-and-escalation.md covering:
- Configuration options
- Escalation curve (attempt 1/2/3+)
- Retry state schema
- Ralph integration

All 60 tests pass.
Commit: 77a9626
