---
description: Sync ticket dependencies from parent links [tf-tickets]
model: openai-codex/gpt-5.3-codex
thinking: high
skill: tf-tickets
---

# /tf-deps-sync

Ensure parent tickets are reflected in `deps` for open tickets.

## Usage

```
/tf-deps-sync [--apply] [--status open|in_progress|all]
```

## Flags

- `--apply`     Apply missing parent deps using `tk dep`
- `--status`    Filter tickets (default: open,in_progress)

## Execution

Follow **TF Tickets Skill → Sync Dependencies**:

1. Load tickets via `tk query` (filter by status).
2. For each ticket with a parent, check if parent is in `deps`.
3. Report missing parent deps and any unknown dep IDs.
4. If `--apply`, add missing parent deps via `tk dep`.
