---
description: Reclassify ticket priorities using P0-P4 rubric
model: minimax/MiniMax-M2.5
thinking: high
---

# /tf-priority-reclassify

Review and reclassify ticket priorities according to the P0-P4 rubric.

## Task Input
- Args: $@

## Usage

```
/tf-priority-reclassify [--apply] [--ids <id1,id2,...>] [--ready] [--status <status>]
```

## Arguments

| Flag | Description |
|------|-------------|
| `--apply` | Apply priority changes (default is dry-run) |
| `--yes` | Skip confirmation prompt (use with `--apply`) |
| `--max-changes N` | Maximum number of tickets to modify (safety cap) |
| `--force` | Apply changes even for ambiguous/unknown classifications |
| `--ids` | Comma-separated list of ticket IDs to process |
| `--ready` | Process all ready tickets |
| `--status` | Filter by ticket status |
| `--tag` | Filter by tag |
| `--include-closed` | Include closed tickets in processing |
| `--include-unknown` | Include tickets with unknown priority in output |
| `--json` | Output results as JSON for scripting |
| `--report` | Write audit trail to `.tf/knowledge/priority-reclassify-{timestamp}.md` |

## Priority Rubric

- **P0**: Critical bug/risk (security, data correctness, OOM, crashes)
- **P1**: Urgent fixes blocking release or major feature work
- **P2**: Real product features (user-facing capabilities)
- **P3**: Important engineering quality / dev workflow improvements
- **P4**: Code cosmetics / refactors / docs / test typing polish

## Execution

1. **Parse arguments** - Determine tickets to process and mode
2. **Fetch tickets** - Load ticket details via `tk show` or equivalent
3. **Classify each ticket** - Apply rubric based on:
   - Title keywords
   - Tags (e.g., `bug`, `feature`, `docs`, `refactor`)
   - Description content
   - Current priority (for reference)
4. **Output results**:
   - Dry-run: Print proposed changes with rationale
   - Apply mode: Update tickets and log changes
5. **Write audit trail** to `.tf/knowledge/priority-reclassify-{timestamp}.md`

## Output Format

```
Ticket    Current  Proposed  Reason
------    -------  --------  ------
abc-1234  P3       P1        Security-related bug (rubric: P0-P1)
def-5678  P2       P2        Product feature (no change)
```

## Notes

- Always default to dry-run unless `--apply` is explicitly provided
- For each ticket, explain which rubric category matched
- Closed/archived tickets are excluded by default