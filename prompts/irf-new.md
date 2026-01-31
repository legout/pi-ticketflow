---
description: Implement ticket with full IRF workflow [irf-workflow +Kimi-K2.5]
model: chutes/moonshotai/Kimi-K2.5-TEE:high
skill: irf-workflow
---

# /irf

Execute the full Implement → Review → Fix → Close workflow with all subagents.

## Usage

```
/irf <ticket-id> [--auto] [--no-research] [--with-research]
```

## Arguments

- `$1` - Ticket ID (e.g., `abc-1234`)
- `$@` - Ticket ID plus optional flags

## Flags

| Flag | Description |
|------|-------------|
| `--auto` / `--no-clarify` | Run headless (no confirmation prompts) |
| `--no-research` | Skip research step |
| `--with-research` | Force enable research step |

## Execution

Follow the **IRF Workflow Skill** procedures, but use subagents for sequential phases:

1. **Re-Anchor Context** - Load AGENTS.md, lessons, ticket details
2. **Research** (optional) - Spawn `researcher` subagent
3. **Implement** - Spawn `implementer` subagent
4. **Parallel Reviews** - Spawn 3 reviewer subagents
5. **Merge Reviews** - Spawn `review-merge` subagent
6. **Fix Issues** - Spawn `fixer` subagent
7. **Close Ticket** - Spawn `closer` subagent

## Comparison with /irf-lite

| Aspect | /irf | /irf-lite |
|--------|------|-----------|
| Subagents | 6-8 | 3 |
| Points of failure | 6-8 | 3 |
| Wall-clock time | Similar | Similar |
| Reliability | Lower | **Higher** |
| Ralph integration | Yes | **Yes** |

## Recommendation

Use `/irf-lite` instead - it has fewer failure points and the same output quality.

This `/irf` command is kept for:
- Compatibility with existing workflows
- Explicit subagent isolation when needed
