---
description: Capture brownfield project status quo [tf-planning +codex-mini]
model: openai-codex/gpt-5.3-codex
thinking: high
skill: tf-planning
---

# /tf-baseline

Capture a status-quo baseline for an existing project.

## Usage

```
/tf-baseline [focus-area]
```

## Arguments

- `$@` - Optional focus area (subsystem to emphasize)

## Examples

```
/tf-baseline
/tf-baseline "authentication system"
```

## Execution

Follow the **TF Planning Skill** "Baseline Capture" procedure:

1. Determine topic ID: `baseline-{repo-name}`
2. Scan project:
   - Read high-signal files (README.md, package.json, etc.)
   - Find entry points, tests, source directories
3. Capture existing tickets (if `tk` is available):
   - Run `tk list --help` to see supported filters
   - Prefer listing open tickets for this repo (tags like `tf`, `baseline`, or `backlog` if supported)
   - If no list command exists, capture `tk ready` output instead
   - Write `existing-tickets.md` with a table of ticket IDs, titles, status, and tags
4. If focus area specified: prioritize scanning that area
5. Write artifacts:
   - `overview.md` - Project summary
   - `baseline.md` - Architecture, components, entry points
   - `risk-map.md` - Technical, dependency, knowledge risks
   - `test-inventory.md` - Test structure and gaps
   - `dependency-map.md` - Dependencies and external services
   - `existing-tickets.md` - Current tickets (from `tk`)
   - `sources.md` - Files scanned
6. Update `index.json`

## Output

Created artifacts in `.tf/knowledge/topics/{topic-id}/`:
- overview.md
- baseline.md
- risk-map.md
- test-inventory.md
- dependency-map.md
- existing-tickets.md
- sources.md

## Use Cases

- Before major refactoring: document current state
- Handoff documentation: capture tribal knowledge
- Risk assessment: identify fragile areas
- Test planning: identify coverage gaps

## Next Steps

- Review baseline artifacts
- Use `/tf-seed` for improvement ideas
- Create tickets via `/tf-backlog`
