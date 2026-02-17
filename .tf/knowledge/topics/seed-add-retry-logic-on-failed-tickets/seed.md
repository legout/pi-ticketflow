# Seed: Retry logic on failed tickets (quality gate) with model escalation

## Vision
When running the Ralph loop, tickets that repeatedly fail to close (e.g., due to quality gate `failOn` severities) should not be re-implemented from scratch indefinitely. Instead, the workflow should detect prior attempts and adapt: focus on what’s still failing and escalate to stronger models to break out of the loop.

## Core Concept
Introduce **retry tracking + escalation config**:
- Detect that a ticket was already attempted (e.g., via artifacts like `close-summary.md` status BLOCKED, or an explicit retry counter file).
- Increment a retry counter per ticket.
- Use an **escalation policy** to switch to more capable models (e.g., `openai-codex/gpt-5.3-codex`) for review/fix (and optionally implement) on retries.
- Optionally skip phases that are unlikely to help on retry (e.g., skip research, or skip implementation if no code changes are needed).

## Key Features
1. **Retry counter**: Persist attempts per ticket across Ralph iterations.
2. **Escalation config**: Configure which models to use for retries (reviewer/fixer/worker).
3. **Phase adaptation**: On retries, focus on review+fix; optionally skip implementation when already implemented.
4. **Convergence behavior**: After N retries, mark ticket as blocked / stop retrying and surface actionable output.
5. **Auditability**: Write artifacts explaining why escalation happened and which models were used.

## Open Questions
- Where should retry state live: ticket artifacts (`.tf/knowledge/tickets/<id>/`), `.tf/ralph/`, or a dedicated `.tf/retries/` store?
- Should retries apply only in Ralph, or also when running `/tf` manually?
- Should we re-run reviews after fixes (post-fix re-review) to make the quality gate meaningful?
- What should the default escalation policy be to balance cost vs success?
- How to avoid flipping back and forth between models/decisions across runs?
