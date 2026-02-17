---
id: pt-rn2w
status: closed
deps: [pt-pcd9]
links: [pt-mdl0, pt-74hd]
created: 2026-02-13T14:36:13Z
type: task
priority: 2
assignee: legout
external-ref: plan-replace-pi-model-switch-extension
tags: [tf, backlog, plan, component:api, component:docs, component:tests, component:workflow]
---
# Add smoke test for /tf chain-prompts workflow (interactive + pi -p)

## Task
Add a lightweight smoke test procedure (and/or automated test) that verifies `/tf <ticket>` works end-to-end with `/chain-prompts`, including non-interactive `pi -p` usage.

## Context
Chaining is implemented by sending multiple user messages and waiting for idle; long-running sequences can regress. We need a repeatable validation step.

## Acceptance Criteria
- [ ] Documented manual smoke test steps in repo docs (or an automated test if feasible)
- [ ] Covers at least: phase ordering, artifact presence, and restore behavior
- [ ] Includes a non-interactive example using `pi -p`

## References
- Plan: plan-replace-pi-model-switch-extension



## Notes

**2026-02-13T17:36:01Z**

Completed smoke test documentation for /tf chain workflow.

Added explicit smoke-test procedure covering:
- deterministic plan resolution via 
- non-interactive I'd be happy to run the `/tf` workflow for you! However, I need a **ticket ID** to proceed.

Would you like me to:

1. **List available tickets** so you can pick one:
   ```bash
   tk ready
   ```

2. **Run with a specific ticket ID** (e.g., `abc-1234`):
   ```
   /tf abc-1234 --dry-run
   ```

3. **Show the chain plan first** without executing:
   ```
   /tf <ticket-id> --plan
   ```

What ticket would you like to process?
- optional phase-command sanity checks
- artifact presence verification
- model restore expectation after chain completion/failure

Documented in docs/workflows.md and aligned command docs.

Commits: f0cd721
