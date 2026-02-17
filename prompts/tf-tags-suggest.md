---
description: Suggest component tags for open tickets [tf-tickets]
model: openai-codex/gpt-5.3-codex
thinking: medium
skill: tf-tickets
---

# /tf-tags-suggest

Suggest missing `component:*` tags for tickets so parallel scheduling is safe.

## Usage

```
/tf-tags-suggest [--apply] [--status open|in_progress|all] [--limit N]
```

## Flags

- `--apply`     Apply suggested tags to ticket files
- `--status`    Filter tickets (default: open,in_progress)
- `--limit`     Limit number of tickets processed

## Execution

Follow **TF Tickets Skill → Suggest Component Tags**:

1. Load tickets via `tk query` (filter by status and limit).
2. Suggest `component:*` tags for tickets missing them.
3. Output a table with rationale.
4. If `--apply`, update `.tickets/<id>.md` frontmatter tags list.
