---
id: plan-retry-logic-quality-gate-blocked
status: approved
last_updated: 2026-02-10
---

# Plan: Retry logic for quality-gate blocked tickets (model escalation)

## Summary

Ralph can repeatedly pick the same ticket when it fails to close (most commonly due to quality gate `failOn` severities). Re-running the full `/tf` chain with the same models can cause thrash and slow convergence.

This plan adds **retry-aware workflow behavior** and a configurable **escalation policy**: on subsequent attempts, switch review/fix (and optionally implement) to more capable models (e.g. `openai-codex/gpt-5.3-codex`), cap per-ticket retries, and record auditable artifacts explaining why escalation occurred.

## Inputs / Related Topics

- Root Seed: [seed-add-retry-logic-on-failed-tickets](topics/seed-add-retry-logic-on-failed-tickets/seed.md)
- Session: seed-add-retry-logic-on-failed-tickets@2026-02-10T12-23-33Z
- Related Spikes:
  - (none yet)

## Requirements

- Persist a **retry counter** per ticket across Ralph iterations.
- Detect "ticket failed to close due to quality gate" deterministically.
- Add **escalation configuration** to settings (per role: reviewer/fixer/worker).
- On retry attempts, switch to escalated models for:
  - at minimum: **fixer** and **reviewer-second-opinion**
  - optionally: **worker** (implementation) when the failure indicates poor implementation quality
- Cap retries per ticket and produce a clear "blocked" outcome when exceeded.
- Write artifacts/log lines that explain:
  - current attempt number
  - which roles were escalated
  - why escalation triggered (e.g. BLOCKED close-summary / failOn severities)

## Constraints

- Must avoid infinite loops in Ralph (bounded retries).
- Backwards compatible: default behavior should remain unchanged when retry logic disabled.
- Configuration must be explicit and versionable in repo settings.
- Do not leak secrets in logs/artifacts.

## Assumptions

- Review severity categories are stable: Critical/Major/Minor/Warnings/Suggestions.
- Model switching is available at runtime via `switch_model`.
- The workflow can reliably read ticket artifacts under `.tf/knowledge/tickets/<ticket-id>/`.

## Risks & Gaps

- **Quality gate semantics**: current gate checks `review.md` counts; without a post-fix re-review, it may still block tickets that are actually fixed.
- **Ticket state semantics**: `tk ready` selection might keep returning tickets that are blocked; we may need an explicit "blocked" marking or skip list.
- **Cost**: escalating to `gpt-5.3-codex` increases spend; needs sensible defaults and caps.

## Work Plan (phases / tickets)

**Decisions made (based on consultant notes):**

1. **Retry state storage**: Store in ticket artifact dir (`.tf/knowledge/tickets/<id>/retry-state.json`) to keep retry data co-located with ticket context. This survives Ralph restarts and is discoverable by both `/tf` and Ralph.

2. **Detection mechanism**: Parse `close-summary.md` for status `BLOCKED`. If present, increment retry counter. Also check if `review.md` has nonzero counts for severities in `workflow.failOn` (as fallback when close-summary missing).

3. **Escalation curve**: Tiered approach:
   - Attempt 1: normal models (current behavior)
   - Attempt 2: escalate fixer only to configured escalation model
   - Attempt 3+: escalate fixer + reviewer-second-opinion + optionally worker (when config enables)

4. **Parallel worker safety**: Document that retry logic assumes `ralph.parallelWorkers: 1` (default). If > 1, document that ticket-level locking is required or disable retry logic.

5. **Counter reset policy**: Reset retry counter to 0 on successful close only. Persist across Ralph restarts otherwise.

6. **Default config values**:
   ```json
   "escalation": {
     "enabled": false,
     "maxRetries": 3,
     "models": {
       "fixer": null,  // null means use current model
       "reviewer-second-opinion": null,
       "worker": null
     }
   }
   ```

7. **Manual `/tf` behavior**: Apply same retry state and escalation logic for manual runs. Add `--retry-reset` flag to force reset for fresh attempt.

8. **Post-fix re-review**: Make mandatory when quality gate is enabled. Add lightweight re-count of review.md severity categories before close (re-run reviewers or parse existing review).

**Ticket breakdown:**

1. **Define retry state + detection**
   - Store retry counter in ticket artifact dir (`retry-state.json`).
   - Detect BLOCKED from `close-summary.md` or nonzero review counts for failOn severities.
   - Document exact detection algorithm.

2. **Add escalation config schema**
   - Extend `settings.json` with `workflow.escalation` (enabled, maxRetries, model overrides per role).
   - Add `--retry-reset` flag to `/tf` for manual override.

3. **Implement retry-aware behavior in `/tf`**
   - Load retry counter at re-anchor.
   - On retry (attempt > 1), switch fixer to escalation model.
   - On retry attempt ≥ 3, escalate reviewer-second-opinion too.
   - Add per-ticket retry cap (mark as BLOCKED and skip after `maxRetries`).

4. **Implement post-fix re-review for gate correctness**
   - After fix step, re-run reviewers or re-parse review.md to verify fixable severities are cleared.
   - Only call `tk close` if post-fix re-review shows zero counts for failOn severities.

5. **Implement Ralph integration**
   - Detect blocked tickets and skip them in `tk ready` query (or mark with tag).
   - Update Ralph progress with retry attempt counts.

6. **Tests + docs**
   - Unit tests for retry counter persistence and escalation model resolution.
   - Docs update: how retries work, how to configure escalation, and how Ralph behaves on blocked tickets.

## Acceptance Criteria

- [ ] Retry counter persists across Ralph iterations and increments on blocked closes.
- [ ] Escalation config can override fixer/reviewer models on retry.
- [ ] Ralph stops retrying a ticket after `maxRetries` and records an actionable summary.
- [ ] Workflow artifacts clearly show attempt number and escalated roles/models.
- [ ] Unit tests cover retry detection and escalation routing.

## Open Questions

- Should retries apply only under Ralph, or also for manual `/tf` runs?
- Should we skip implementation on retries by default, or always re-run with an escalated worker?
- Do we need an explicit ticket status/tag change to prevent `tk ready` from selecting blocked tickets?
- What should default escalation models be (cost vs effectiveness)?

---

## Consultant Notes (Metis)

- 2026-02-10: **Gap - Detection mechanism underspecified**: The plan mentions detecting "failed due to quality gate" via close-summary.md or review.md, but doesn't specify the exact logic. Recommend: parse close-summary.md for status BLOCKED, or check if review.md has nonzero counts for severities in workflow.failOn. Document the exact detection algorithm.

- 2026-02-10: **Gap - Retry state location undecided**: Three options listed but no decision. Recommend: store in ticket artifact dir (`.tf/knowledge/tickets/<id>/retry-state.json`) to keep retry data co-located with ticket context. This survives Ralph restarts and is discoverable by both `/tf` and Ralph.

- 2026-02-10: **Gap - Escalation curve undefined**: Plan says "on retry attempts" but doesn't specify if escalation happens immediately on 2nd attempt or gradually. Recommend: simple tiered approach - attempt 1 = normal models, attempt 2 = escalate fixer only, attempt 3+ = escalate fixer + reviewer-second-opinion + optionally worker.

- 2026-02-10: **Gap - Parallel worker race condition**: Ralph config allows `parallelWorkers > 1`. If two workers pick the same ticket simultaneously, retry counters could race. Recommend: document that retry logic assumes `parallelWorkers: 1` (default), or implement ticket-level locking.

- 2026-02-10: **Gap - Counter reset policy**: When does retry count reset to 0? After successful close? After manual ticket edit? After time threshold? Recommend: reset on successful close only; persist across Ralph restarts otherwise.

- 2026-02-10: **Gap - Default config values missing**: Plan mentions escalation config but doesn't specify defaults. Recommend: `enabled: false` (backwards compatible), `maxRetries: 3`, escalation models default to current models (no escalation unless explicitly configured).

- 2026-02-10: **Ambiguity - Manual `/tf` behavior**: Open question asks if retries apply to manual runs. Recommend: yes, use same retry state and escalation logic so manual intervention benefits from accumulated context. Add `--retry-reset` flag to force reset if user wants fresh attempt.

- 2026-02-10: **Risk — Post-fix re-review critical**: Current quality gate checks review.md counts from *before* fixes. Without post-fix re-review, a ticket with fixable issues will always show nonzero counts and block forever, regardless of retries. Recommend: make post-fix re-review **mandatory** when quality gate is enabled, not optional. This is prerequisite for retry logic to work correctly.

---

## Revision Note (2026-02-10)

Revised plan to address all 8 consultant gaps:

1. **Detection mechanism**: Specified exact algorithm (parse close-summary.md for BLOCKED, fallback to review.md counts).
2. **Retry state storage**: Decided on ticket artifact dir (`retry-state.json`) for co-location.
3. **Escalation curve**: Defined tiered approach (attempts 1/2/3+ with different escalation levels).
4. **Parallel worker safety**: Documented assumption of `parallelWorkers: 1`; added warning for >1.
5. **Counter reset policy**: Specified reset on successful close only.
6. **Default config values**: Added explicit defaults with `enabled: false` for backwards compatibility.
7. **Manual `/tf` behavior**: Clarified that retry logic applies to manual runs too; added `--retry-reset` flag.
8. **Post-fix re-review**: Upgraded from "optional" to "mandatory" when quality gate enabled; made this a separate ticket (#4).

## Reviewer Notes (Momus)

- 2026-02-10: PASS (high-accuracy review)
  - Requirements, constraints, and risks were coherent; retry state, detection, escalation, and Ralph integration are fully specified.
  - Gap decisions (state storage, detection logic, escalation curve, reset policy, manual `/tf` behavior, post-fix re-review) are all resolved and reflected in the work plan, so the plan is implementable.
