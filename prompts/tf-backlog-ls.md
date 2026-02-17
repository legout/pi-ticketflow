---
description: List backlog status and tickets [tf-planning +codex-mini]
model: chutes/zai-org/GLM-4.7-Flash
thinking: medium
skill: tf-planning
---

# /tf-backlog-ls

Show backlog status and corresponding tickets for seed/baseline/plan topics.

## Usage

```
/tf-backlog-ls [topic-id-or-path]
```

## Arguments

- `$1` - Optional topic ID (`seed-*`, `baseline-*`, or `plan-*`) or path to topic directory
- If omitted: list all seed/baseline/plan topics with backlog status

## Examples

```
/tf-backlog-ls
/tf-backlog-ls seed-build-a-cli
/tf-backlog-ls plan-auth-rewrite
/tf-backlog-ls baseline-myapp
/tf-backlog-ls .tf/knowledge/topics/baseline-myapp/
```

## Execution

Follow the **TF Planning Skill** "Backlog Listing" procedure:

1. Resolve `knowledgeDir`
2. If topic provided: show full backlog table + summary
3. If no topic: list all seed/baseline/plan topics with backlog status
4. Mark topics without `backlog.md` as **unticketed**
