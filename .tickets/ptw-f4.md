---
id: ptw-f4
status: closed
deps: []
links: []
created: 2026-02-05T15:25:00Z
type: task
priority: 3
assignee: legout
external-ref: ptw-6dza
tags: [tf, followup]
---
# Add examples for hint-based override and --no-deps

## Origin
From review of ticket: ptw-6dza
File: prompts/tf-backlog.md

## Issue
The Examples section in prompts/tf-backlog.md could benefit from:
1. An explicit example of the hint-based override behavior to help users understand when/how keyword detection works
2. An example showing `--no-deps` usage for better discoverability

## Severity
Suggestion

## Acceptance Criteria
- [ ] Add example showing hint-based override (keyword detection) behavior
- [ ] Add example showing `--no-deps` flag usage
- [ ] Ensure examples are clear and demonstrate the value of these features

## Notes

**2026-02-05T16:56:01Z**

Added two example sections to prompts/tf-backlog.md:

1. Hint-Based Override Example - Shows how keywords (setup/configure, define/design, implement, test) affect ticket ordering with a concrete example

2. --no-deps Example - Shows standalone usage for independent tasks

Commit: 2377a4b

Review: 0 Critical, 0 Major (reported issue was already correct in implementation), 2 Minor, 1 Suggestion
