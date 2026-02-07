# Seed: Auto-use active planning session inputs in `/tf-backlog`

## Vision

When a user starts a planning session with `/tf-seed`, the workflow intent is that subsequent planning commands operate on that session’s context. For `/tf-backlog`, requiring the user to pass an explicit topic-id/path is redundant and error-prone; the command should automatically use the active session’s seed (and related spikes/plan) when available.

## Core Concept

If `.tf/knowledge/.active-planning.json` exists with `state: active`, then `/tf-backlog` should:

- default the backlog topic to `root_seed`
- incorporate session-linked artifacts (`spikes[]`, `plan`) as additional inputs/context
- still allow explicit override via an argument (topic-id/path)

## Key Features

1. **Argument optionality**: `/tf-backlog` with no argument uses active session’s `root_seed` when present.
2. **Session-aware inputs**: backlog generation consults `plan.md` (if `plan` exists) and `spike.md` docs (if any spikes exist) for additional requirements/constraints.
3. **Override behavior**: if user passes an explicit topic-id/path, it takes precedence; session is not used unless explicitly requested.
4. **Clear UX**: emit a notice indicating what inputs were used (seed id + spikes + plan).

## Open Questions

- Should “use session inputs automatically” also apply when an explicit topic-id is supplied but matches the session root seed?
- How should conflicts be resolved when plan requirements diverge from seed/spike statements (precedence rules)?
- Should we add a `--use-session` / `--no-session` flag for `/tf-backlog` to make behavior explicit?
