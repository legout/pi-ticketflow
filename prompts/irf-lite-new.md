---
description: Implement ticket with simplified IRF workflow [irf-workflow +Kimi-K2.5]
model: chutes/moonshotai/Kimi-K2.5-TEE:high
skill: irf-workflow
---

# /irf-lite

Execute the simplified Implement → Review → Fix → Close workflow for a ticket.

## Usage

```
/irf-lite <ticket-id> [--auto] [--no-research] [--with-research]
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

Follow the **IRF Workflow Skill** procedures:

1. **Re-Anchor Context** - Load AGENTS.md, lessons, ticket details
2. **Research** (optional) - MCP tools for knowledge gathering
3. **Implement** (model-switch) - Code changes with quality checks
4. **Parallel Reviews** (subagents) - 3 reviewers in parallel
5. **Merge Reviews** (model-switch) - Deduplicate and consolidate
6. **Fix Issues** (model-switch) - Apply fixes
7. **Close Ticket** - Add note and close in `tk`
8. **Ralph Integration** (if active) - Update progress, extract lessons

## Output Artifacts

- `implementation.md` - Implementation summary
- `review.md` - Consolidated review
- `fixes.md` - Fixes applied
- `close-summary.md` - Final summary

Ralph files (if `.pi/ralph/` exists):
- `.pi/ralph/progress.md` - Updated
- `.pi/ralph/AGENTS.md` - May be updated

## Notes

- This is the **recommended** workflow (fewer subagents, more reliable)
- Uses `switch_model` for sequential phases instead of subagents
- Only the parallel review step spawns subagents
- Automatically integrates with Ralph loop if initialized
