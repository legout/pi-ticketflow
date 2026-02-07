---
id: pt-gn5z
status: closed
deps: [pt-zoqp]
links: [pt-ctov]
created: 2026-02-06T13:51:22Z
type: task
priority: 2
assignee: legout
external-ref: seed-pi-command-reclassify-priorities
tags: [tf, backlog, component:agents, component:cli, component:config, component:docs, component:workflow]
---
# Design + setup /tf-priority-reclassify prompt and Python entrypoint

## Task
Add a new Pi prompt command (e.g. `/tf-priority-reclassify`) and a minimal Python entrypoint to run the reclassification logic.

## Context
Other Ticketflow Pi commands live under `prompts/`, and complex logic is typically implemented in `tf_cli/`.

## Acceptance Criteria
- [ ] New prompt markdown exists in `prompts/` with usage + options.
- [ ] New `tf new ...` subcommand skeleton exists and prints `--help`.
- [ ] Command accepts `--apply` (default dry-run) and `--ids ...` (at least).

## Constraints
- No priority updates are performed in this ticket (scaffolding only).

## References
- Seed: seed-pi-command-reclassify-priorities


## Notes

**2026-02-06T14:05:59Z**

## Implementation Complete

Created the `/tf-priority-reclassify` Pi prompt and Python CLI entrypoint.

### Files Added
- `prompts/tf-priority-reclassify.md` - Pi prompt with P0-P4 rubric and usage docs
- `tf_cli/priority_reclassify_new.py` - Python entrypoint with classification logic
- Updated `tf_cli/cli.py` and `tf_cli/new_cli.py` to register the command

### Features
- Dry-run by default (`--apply` required for changes)
- Multiple selection modes: `--ids`, `--ready`, `--status`, `--tag`
- P0-P4 rubric-based classification
- Audit trail written to `.tf/knowledge/priority-reclassify-{timestamp}.md`
- Closed tickets automatically excluded

### Verification
```bash
python -m tf_cli priority-reclassify --help
python -m tf_cli new priority-reclassify --help
```

Commit: 8456669
