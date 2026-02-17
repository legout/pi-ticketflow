---
description: Create tickets from seed, baseline, or plan artifacts [tf-planning +codex-mini]
model: openai-codex/gpt-5.3-codex
thinking: high
skill: tf-planning
---

# /tf-backlog

Generate small, actionable tickets from a seed, baseline, or plan topic.

## Usage

```
/tf-backlog [<topic-id-or-path>] [--no-deps] [--no-component-tags] [--no-links] [--links-only]
```

## Arguments

- `$1` topic ID/path (`seed-*`, `baseline-*`, `plan-*`)
- If omitted:
  - use active session root seed when available
  - otherwise auto-locate when exactly one valid topic exists

## Flags

- `--no-deps`: skip dependency inference
- `--no-component-tags`: skip component tag assignment
- `--no-links`: skip ticket linking
- `--links-only`: do not create tickets; only link tickets already in `backlog.md`

## Deterministic Helpers (required)

Use Python modules instead of inline ad-hoc scripts:

- `tf.ticket_factory` for scoring, creation, dependency/link application, and `backlog.md`
- `tf.session_store` for active session resolution and session archive/finalization

## Execution Contract

1. Parse flags and resolve target topic.
2. If a planning session is active, load root seed + optional plan/spikes as extra context.
3. Read source artifacts for the topic type and derive concise ticket definitions.
4. Create/update backlog using `tf.ticket_factory`:
   - `score_tickets`
   - `create_tickets`
   - `apply_dependencies` unless `--no-deps`
   - `apply_links` unless `--no-links`
   - `write_backlog_md`
5. In `--links-only` mode:
   - do not create tickets
   - load existing backlog tickets and apply only linking updates
6. If session-backed run succeeded:
   - archive session snapshot under `.tf/knowledge/sessions/`
   - clear active session pointer
   - emit archive summary
7. If creation fails mid-run:
   - preserve active session
   - write error snapshot
   - report partial progress

## Ticket Quality Rules

- Keep tickets small (about 1-2 hours each).
- Use explicit acceptance criteria.
- Avoid duplicates from existing backlog/current open tickets.
- Include references back to source topic (`external-ref`).

## Output

- `tk` tickets created/updated
- `backlog.md` in topic directory
- optional dependency edges and links
- session archive/failure snapshot when session mode is active

## Next Step

```
/tf <ticket-id>
```
