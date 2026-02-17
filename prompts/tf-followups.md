---
description: Create tickets from review warnings/suggestions [tf-planning +codex-mini]
model: openai-codex/gpt-5.3-codex
thinking: medium
skill: tf-planning
---

# /tf-followups

Create follow-up tickets from Warnings and Suggestions in a review.

## Usage

```
/tf-followups <review-path-or-ticket-id>
```

## Arguments

- `$1` - Path to review.md or original ticket ID
- If omitted: uses `./review.md` if it exists

## Examples

```
/tf-followups ./review.md
/tf-followups abc-1234
```

## Execution

Follow the **TF Planning Skill** "Follow-up Creation" procedure:

1. Resolve review path:
   - If path: use directly
   - If ticket ID: prefer `.tf/knowledge/tickets/{ticket-id}/review.md` when it exists; otherwise search `/tmp/pi-chain-runs`
   - If empty: check `./review.md` (or the current ticket artifact directory)
2. Parse review:
   - Extract Warnings section
   - Extract Suggestions section
3. For each item, create ticket:
   ```bash
   tk create "<title>" \
     --description "## Origin\nFrom review of: {ticket}\nFile: {file}\nLine: {line}\n\n## Issue\n{description}" \
     --tags tf,followup \
     --priority 3
   ```
4. Write `followups.md` documenting created tickets (same directory as the review when possible)

## followups.md Template

When creating follow-up tickets, ALWAYS write a `followups.md` file in the ticket artifact directory. This serves as an idempotency marker for the scan command.

### Standard Format (when follow-ups are created)

```markdown
# Follow-ups: {origin-ticket-id}

## Origin
- **Original Ticket:** {ticket-id}
- **Review Path:** {path-to-review.md}
- **Generated:** {ISO-8601-timestamp}

## Created Follow-up Tickets

### From Warnings
| Ticket ID | Title | File | Line |
|-----------|-------|------|------|
| {id} | {title} | {file} | {line} |

### From Suggestions
| Ticket ID | Title | File | Line |
|-----------|-------|------|------|
| {id} | {title} | {file} | {line} |

## Summary
- {N} ticket(s) created from Warnings
- {M} ticket(s) created from Suggestions
- All tagged with: tf, followup, {origin-ticket-id}-followup
```

### No Follow-ups Needed Format

Write this when:
- `review.md` file is missing or cannot be found
- Review has no Warnings section or Warnings section is empty/(none)
- Review has no Suggestions section or Suggestions section is empty/(none)

```markdown
# Follow-ups: {origin-ticket-id}

## Origin
- **Original Ticket:** {ticket-id}
- **Review Path:** {path-to-review.md-or-"not-found"}
- **Generated:** {ISO-8601-timestamp}

## Status
**No Follow-ups Needed**

## Details
- Warnings found: (none)
- Suggestions found: (none)

## Rationale
{explanation: e.g., "Review file not found at expected path" or "No actionable Warnings or Suggestions in review"}
```

## Ticket Description Template

```markdown
## Origin
From review of ticket: {original_ticket_id}
File: {file_path}
Line: {line_number}

## Issue
{description from review}

## Severity
{Warning or Suggestion}

## Acceptance Criteria
- [ ] {specific fix}
- [ ] Tests updated if applicable
- [ ] No regressions
```

## Output

- Tickets created in `tk` (tagged: tf, followup)
- `followups.md` with summary (written in the ticket artifact directory when available)

## Notes

- Warnings = technical debt, should address
- Suggestions = improvements, nice to have
- Both are out of scope for the original ticket
- Priority is lower (3) than implementation tickets
