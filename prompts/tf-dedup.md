---
description: Suggest duplicate tickets for review [tf-tickets]
model: openai-codex/gpt-5.3-codex
thinking: high
skill: tf-tickets
---

# /tf-dedup

Find likely duplicate tickets among open work.

## Usage

```
/tf-dedup [--status open|in_progress|all] [--limit N] [--link]
```

## Flags

- `--status`  Filter tickets (default: open,in_progress)
- `--limit`   Limit number of tickets considered
- `--link`    Link suggested duplicates with `tk link`

## Execution

Follow **TF Tickets Skill → Deduplicate Tickets**:

1. Load tickets via `tk query` (filter by status and limit).
2. Group likely duplicates by parent + title similarity.
3. Output candidate clusters with rationale.
4. If `--link`, run `tk link` for each suggested pair.
