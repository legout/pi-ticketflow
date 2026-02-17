---
id: pt-2rjt
status: closed
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


## Notes

**2026-02-17T16:50:29Z**

Implemented worktree lifecycle for /ralph-loop dispatch runs.

Changes:
- Create per-ticket worktree before launch
- Run dispatch with worktree as cwd  
- Merge+close on success, cleanup on failure
- Preserve worktree on merge failure for manual resolution
- Signal handler cleanup for interrupted runs
- Path validation for security

Commit: d8c3418e
Review: 4 Critical, 6 Major issues addressed
Follow-ups: Session status detection, tests needed
