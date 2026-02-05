# Implementation: ptw-f5

## Summary
Documented the behavior of out-of-order ticket creation in the default dependency chain logic. Added clear guidance on how the chain works and how to manually correct dependencies when tickets are created non-sequentially.

## Files Changed
- `skills/tf-planning/SKILL.md` - Added "Out-of-order creation" subsection under Seed mode dependency inference
- `prompts/tf-backlog.md` - Added matching documentation in the prompt template

## Key Decisions
- Added the documentation inline with the existing dependency chain explanation rather than as a separate note, keeping the information co-located with the relevant procedure
- Included concrete example with ticket IDs (ticket 5 created before ticket 3) to make the behavior concrete
- Provided exact `tk dep` commands for manual correction to make the guidance actionable

## Changes Detail

### skills/tf-planning/SKILL.md
Added after the default chain description:
> **Out-of-order creation**: The chain is based on creation sequence, not ticket IDs. If ticket 5 is created before ticket 3, ticket 5 will have no dependency (first created) and ticket 3 will depend on ticket 5 (if created second). To correct this, manually adjust with `tk dep <ticket-3> <ticket-5>` and `tk dep <ticket-5> --remove`.

### prompts/tf-backlog.md
Added matching documentation:
> **Out-of-order creation**: The chain reflects creation sequence, not ticket ID order. If you create ticket 5 before ticket 3, ticket 5 becomes the chain head and ticket 3 depends on it. To fix: `tk dep <ticket-3> <ticket-5>` then `tk dep <ticket-5> --remove`.

## Tests Run
- Documentation-only change; no code tests required
- Verified markdown syntax is valid

## Verification
1. Read the updated sections in both files to confirm clarity
2. Check that the `tk dep --remove` syntax matches the CLI's actual capabilities
