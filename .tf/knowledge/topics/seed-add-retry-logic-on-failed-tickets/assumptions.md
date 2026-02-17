# Assumptions

- Quality gate failures are detectable from existing artifacts (e.g., `close-summary.md` or `review.md` counts).
- It is acceptable to spend more tokens/$$ on retries than on first attempts.
- The workflow can reliably switch models mid-chain via `switch_model`.
- The ticket implementation can be treated as mostly idempotent (re-running should not break code).
