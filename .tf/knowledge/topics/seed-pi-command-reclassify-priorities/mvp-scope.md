# MVP Scope

## In Scope
- A new Pi command that:
  - selects tickets (explicit IDs and/or a simple query like “ready”)
  - computes a proposed P0–P4 classification using the rubric
  - prints a per-ticket explanation
  - supports `--apply` to update the ticket priority via `tk`

## Out of Scope (for MVP)
- Machine-learning / embedding-based classification.
- Full configuration UI; advanced rule authoring.
- Automatic tagging / dependency changes.
- Cross-project triage or integration with external issue trackers.
