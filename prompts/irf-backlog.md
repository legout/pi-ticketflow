---
description: Create tickets from seed artifacts [irf-planning +codex-mini]
model: openai-codex/gpt-5.1-codex-mini
skill: irf-planning
---

# /irf-backlog

Generate small, actionable implementation tickets from seed artifacts.

## Usage

```
/irf-backlog <seed-path-or-topic-id>
```

## Arguments

- `$1` - Path to seed directory or topic ID
- If omitted: auto-locates seed if exactly one exists

## Examples

```
/irf-backlog seed-build-a-cli
/irf-backlog .pi/knowledge/topics/seed-build-a-cli/
```

## Execution

Follow the **IRF Planning Skill** "Backlog Generation" procedure:

1. Locate seed (by path or topic ID)
2. Read seed artifacts (seed.md, mvp-scope.md, etc.)
3. Create 5-15 small tickets (1-2 hours each, 30 lines max)
4. For each ticket:
   - Extract single focused task
   - Summarize context in 2-3 sentences
   - List 3-5 acceptance criteria
   - Include relevant constraints
   - Create via `tk create`
5. Write `backlog.md` with ticket summary

## Ticket Template

```markdown
## Task
<Single-sentence description>

## Context
<2-3 sentences from seed>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Constraints
<Relevant constraints>

## References
- Seed: <topic-id>
```

## Output

- Tickets created in `tk`
- `backlog.md` written to topic directory

## Next Steps

Start implementation:
```
/irf-lite <ticket-id>
```
