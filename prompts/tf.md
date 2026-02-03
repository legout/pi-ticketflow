---
description: Implement ticket with IRF workflow [tf-workflow +Kimi-K2.5]
model: chutes/moonshotai/Kimi-K2.5-TEE
thinking: high
skill: tf-workflow
---

# /tf

Execute the standard Implement → Review → Fix → Close workflow for a ticket.

## Usage

```
/tf <ticket-id> [--auto] [--no-research] [--with-research] [--plan] [--dry-run]
             [--create-followups] [--simplify-tickets] [--final-review-loop]
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
| `--plan` / `--dry-run` | Print resolved chain and exit without running agents |
| `--create-followups` | Run `/tf-followups` on merged review output |
| `--simplify-tickets` | Run `/simplify --create-tickets --last-implementation` if available |
| `--final-review-loop` | Run `/review-start` after the chain if available |

## Execution

Follow the **TF Workflow Skill** procedures:

1. **Re-Anchor Context** - Load AGENTS.md, lessons, ticket details
2. **Research** (optional) - MCP tools for knowledge gathering
3. **Implement** (model-switch) - Code changes with quality checks
4. **Parallel Reviews** (optional) - Reviewer subagents when enabled
5. **Merge Reviews** (optional) - Deduplicate and consolidate
6. **Fix Issues** (optional) - Apply fixes when enabled
7. **Follow-ups** (optional) - Create follow-up tickets when requested
8. **Close Ticket** (optional) - Add note and close in `tk` when allowed
9. **Final Review Loop** (optional) - Run `/review-start` when requested
10. **Simplify Tickets** (optional) - Run `/simplify` follow-on if available
11. **Ralph Integration** (if active) - Update progress, extract lessons

## Output Artifacts

Written under `.tf/knowledge/tickets/<ticket-id>/`:
- `research.md` - Ticket research (if any)
- `implementation.md` - Implementation summary
- `review.md` - Consolidated review
- `fixes.md` - Fixes applied
- `followups.md` - Follow-up tickets (if `--create-followups`)
- `close-summary.md` - Final summary
- `chain-summary.md` - Artifact index (closer)
- `files_changed.txt` - Tracked changed files
- `ticket_id.txt` - Ticket ID

Ralph files (if `.tf/ralph/` exists):
- `.tf/ralph/progress.md` - Updated
- `.tf/ralph/AGENTS.md` - May be updated

## Notes

- This is the standard workflow (model-switch for sequential phases)
- Only the parallel review step spawns subagents
- The close step stages/commits only paths from `files_changed.txt` plus the ticket artifact directory
- `/tf-lite` is a deprecated alias that runs the same workflow
