# Review: pt-8qk8

## Critical (must fix)
- `tf/ralph.py:840-975`, `tf/ralph.py:2623-2640` - Recovery is invoked at startup, but dispatch lifecycle persistence is not fully wired end-to-end (register/update/remove) for all launch/completion paths, so orphan recovery + TTL pruning can be ineffective in real flows. **Sources:** reviewer-general
- `tf/ralph_completion.py:59-97`, `tf/ralph/session_recovery.py:257-299,357-429` - Orphan detection/liveness checks rely on child-process semantics and PID-only checks; this can misclassify foreign running processes (or PID reuse) and leave true orphans alive or mark wrong sessions. **Sources:** reviewer-general, reviewer-second-opinion

## Major (should fix)
- `tf/ralph.py:2631-2641` - Startup recovery can run during dry-run and still mutate state/terminate processes; dry-run should be non-mutating. **Sources:** reviewer-general
- `tf/ralph.py:2635` - TTL config parsing uses raw `int(...)`; invalid values can raise and abort startup. Use safe resolver/validation. **Sources:** reviewer-general
- `tf/ralph/session_recovery.py:438-454` - Worktree cleanup path validation is insufficient against tampered state; enforce cleanup strictly under allowed roots. **Sources:** reviewer-general
- `tf/ralph/session_recovery.py:102-155,214-220,242-259,281-298` - Session-state read/modify/write has no file locking and no atomic write protection; concurrent writers can lose/corrupt state. **Sources:** reviewer-general, reviewer-second-opinion

## Minor (nice to fix)
- `tf/ralph/session_recovery.py:331-344` - `current_pid` parameter is documented but unused. **Sources:** reviewer-general
- `tf/ralph/session_recovery.py:334-469` - Cleanup success reporting is optimistic: failures in worktree removal/state update can still be surfaced as successful orphan cleanup. **Sources:** reviewer-general, reviewer-second-opinion
- `tf/ralph.py:31-37,1203-1217` - Unused recovery symbols/imports indicate incomplete integration and reduce maintainability. **Sources:** reviewer-general
- `tf/ralph/session_recovery.py:26` + direct caller paths - TTL config handling is split; direct calls can ignore configured override unless caller resolves it first. **Sources:** reviewer-second-opinion

## Warnings (follow-up ticket)
- `tests/` - No dedicated tests cover session-recovery integration paths (startup cleanup, lifecycle wiring, TTL pruning, liveness edge cases). **Sources:** reviewer-general, reviewer-second-opinion
- `tf/ralph/session_recovery.py:395-432` - Non-terminal/running sessions are never aged out, which can allow state-file growth over long-running/restart-heavy environments. **Sources:** reviewer-second-opinion
- `tf/ralph/session_recovery.py:96-114` - ISO timestamp parsing portability/version behavior is somewhat fragile; consider stricter parsing. **Sources:** reviewer-second-opinion

## Suggestions (follow-up ticket)
- Wire lifecycle persistence uniformly: register on launch, update on terminal outcomes, and remove/archive consistently across serial + parallel paths.
- Harden liveness checks for orphan detection (distinguish owned child vs foreign process; validate process identity beyond PID).
- Add configurable orphan grace period to reduce false positives during quick restarts.
- Add session-recovery metrics (cleanup duration, prune counts/ages, cleanup failure rates) for operability.
- Create timestamped backup before recovery mutations and document state schema/version migration policy.

## Summary Statistics
- Critical: 2
- Major: 4
- Minor: 4
- Warnings: 3
- Suggestions: 5
