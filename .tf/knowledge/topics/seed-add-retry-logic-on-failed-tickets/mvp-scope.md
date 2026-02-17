# MVP Scope

## In Scope
- Persist a retry counter per ticket (minimally: detect and count BLOCKED close summaries).
- Add escalation configuration to settings (models for reviewer/fixer/worker on retries).
- In `/tf` skill logic: on retry, switch reviewer-second-opinion and fixer to a stronger model.
- In Ralph loop: cap retries per ticket and stop thrashing (surface a clear “blocked” outcome).

## Out of Scope (for MVP)
- Full post-fix re-review loop with automatic gate verification.
- Automatic ticket status transitions (e.g., moving to a dedicated “blocked” column).
- Sophisticated heuristics for skipping implementation beyond simple “already implemented” detection.
- Cost-optimized dynamic routing across many models.
