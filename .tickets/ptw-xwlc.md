---
id: ptw-xwlc
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
# Update tf-backlog to apply component tags by default

## Task
Update the /tf-backlog workflow to automatically assign `component:*` tags to newly created tickets.

## Context
Ralph parallel processing and backlog filtering rely on consistent component tags. Today tags are added only via manual follow-ups (e.g., /tf-tags-suggest).

## Acceptance Criteria
- [ ] /tf-backlog assigns at least one `component:*` tag to each created ticket when it can infer one.
- [ ] Tickets without a confident component are left untagged (no random tagging).
- [ ] Behavior is documented, including how to re-run tagging via /tf-tags-suggest.

## Constraints
- Must not break existing /tf-backlog behavior.

## References
- Seed: seed-backlog-deps-and-tags


## Notes

**2026-02-05T16:40:16Z**

Implemented: Updated /tf-backlog to apply component:* tags by default

Changes:
- Modified prompts/tf-backlog.md to enable automatic component tagging
- Component tags are now applied during ticket creation using tf_cli.component_classifier
- Added --no-component-tags flag for opt-out
- All 24 component classifier tests pass

The classifier analyzes ticket titles/descriptions and assigns tags like component:cli, component:tests, etc. when confident matches are found. Tickets without confident matches remain untagged.

Documentation includes fallback path via /tf-tags-suggest --apply for re-tagging.
