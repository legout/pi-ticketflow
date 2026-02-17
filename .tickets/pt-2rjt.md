---
id: pt-2rjt
status: open
deps: [pt-9hgu]
links: []
created: 2026-02-17T14:36:52Z
type: task
priority: 2
assignee: legout
external-ref: ralph-loop-parity
tags: [tf, ralph, component:workflow, component:git]
---
# Add worktree lifecycle to /ralph-loop dispatch runs

Create per-ticket worktree before launch, run dispatch in worktree cwd, and merge+close on success or cleanup on failure. Keep semantics compatible with existing Ralph safety.

## Acceptance Criteria

Worktree created per ticket; dispatch launched with worktree cwd; success merges & removes worktree; failure cleans up safely; merge failure preserves worktree and marks ticket failed.

