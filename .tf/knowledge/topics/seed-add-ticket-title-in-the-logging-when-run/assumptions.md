# Assumptions

- Ralph already has a single place where ticket-scoped logs are produced (or can be routed) so the formatting change can be centralized.
- The ticket title is obtainable either from:
  - an existing in-memory ticket structure, or
  - a single `tk` query per ticket (with caching).
- Adding the title does not break downstream consumers of logs (or only affects `--verbose`).
