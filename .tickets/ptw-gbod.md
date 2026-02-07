---
id: ptw-gbod
status: closed
deps: []
links: []
created: 2026-02-05T14:00:22Z
type: task
priority: 2
assignee: legout
external-ref: seed-backlog-deps-and-tags
tags: [tf, backlog]
---
# Add tf-backlog args for disabling auto deps/tags/links

## Task
Add and document optional arguments for /tf-backlog to disable automatic behaviors: deps, component tags, links.

## Context
Automatic inference can fail or be undesirable for some topics. Users need simple opt-outs and should be able to use fallback commands instead.

## Acceptance Criteria
- [ ] /tf-backlog supports opt-outs (e.g., `--no-deps`, `--no-component-tags`, `--no-links`).
- [ ] Help/docs updated with examples.
- [ ] Defaults remain enabled.

## Constraints
- Parsing should be robust (ignore unknown flags with warning).

## References
- Seed: seed-backlog-deps-and-tags


## Notes

**2026-02-05T16:04:49Z**

Implemented --no-component-tags flag for /tf-backlog

Changes:
- Updated prompts/tf-backlog.md with new flag and examples
- Updated skills/tf-planning/SKILL.md with component tag procedure step
- Updated docs/commands.md with flag documentation and examples

Commit: f703c87

All acceptance criteria met:
- /tf-backlog supports --no-deps, --no-component-tags, --no-links
- Help/docs updated with examples showing all flags
- Defaults remain enabled (opt-out flags)
