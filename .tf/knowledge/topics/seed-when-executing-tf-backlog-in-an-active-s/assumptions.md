# Assumptions

- The active session file `.tf/knowledge/.active-planning.json` is the source of truth for session context.
- Session-linked topics (spikes/plan) live under `.tf/knowledge/topics/<topic-id>/`.
- Backlog generation already has an internal structure that can be extended to read additional docs without rewriting ticket creation logic.
