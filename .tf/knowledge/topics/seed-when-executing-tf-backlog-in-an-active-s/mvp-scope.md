# MVP Scope

## In Scope

- If `/tf-backlog` is invoked without a topic argument and an active session exists, infer topic = `root_seed`.
- When session has `plan` and/or `spikes`, include their docs as optional context for backlog ticket descriptions.
- Print a short “inputs used” summary (seed, spikes count, plan present).

## Out of Scope (for MVP)

- Complex precedence/rules engine for resolving conflicting statements across docs.
- New interactive UI for selecting among multiple sessions.
- Auto-creating spikes/plan.
