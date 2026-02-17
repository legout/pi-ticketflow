# Review: pt-0v53

## Critical (must fix)
- `tf/ralph.py:1244-1364` - Worktree branch is created from `HEAD` rather than an explicit merge target base (`main`/`master`), which can pull unrelated commits into the merge path when Ralph starts from a feature branch. (sources: reviewer-general, reviewer-second-opinion)
- `tf/ralph.py:1244-1291` - Potential stale-worktree race in pre-cleanup path: a prior worktree can appear removed to git while directory state remains inconsistent for subsequent `worktree add`. (source: reviewer-second-opinion)
- `tf/ralph.py:1424` - Branch naming collision risk with fixed name `ralph/{ticket}` under concurrent/retry scenarios. (source: reviewer-second-opinion)

## Major (should fix)
- `tf/ralph.py:1380-1397,1996-2067,2358-2437` - Success can be reported even when `git worktree remove` fails after merge; stale worktrees/metadata may accumulate while ticket is treated as complete. (sources: reviewer-general, reviewer-second-opinion)
- `tf/ralph.py:1153-1195,1833-1866` - Restart/timeout paths may reuse a non-refreshed worktree, allowing failed-attempt state to leak into retries. (source: reviewer-second-opinion)
- `tf/ralph.py:1461-1495` - Merge-failure/cleanup UX is under-specified (limited operator guidance for manual recovery when conflicts occur). (source: reviewer-second-opinion)

## Minor (nice to fix)
- `tf/ralph.py:1342-1359` - Extra checkout of `main`/`master` inside the ticket worktree appears unnecessary and its result is not used. (source: reviewer-general)
- `tf/ralph.py:1467` - `--no-ff` merge policy is not documented inline, making intent less clear for maintainers. (source: reviewer-second-opinion)
- `tf/ralph.py:1519-1524` - Forced branch deletion (`-D`) in cleanup path is aggressive; clarify/document intent. (source: reviewer-second-opinion)
- `tf/ralph.py:1440-1444` - Direct filesystem-removal fallback can mask actionable cleanup errors. (source: reviewer-second-opinion)

## Warnings (follow-up ticket)
- `tf/ralph.py:1244-1440,1996-2067,2358-2430` - Missing focused automated tests for worktree lifecycle behavior (base selection, merge/cleanup semantics). (sources: reviewer-general, reviewer-second-opinion)
- `tf/ralph.py:1066-1071` - Parallel-mode worktree logic remains separate from new serial helpers (risk of divergence). (source: reviewer-second-opinion)
- `tf/ralph.py:1153` - No explicit interrupt/signal cleanup strategy documented for dispatch worktrees. (source: reviewer-second-opinion)

## Suggestions (follow-up ticket)
- `tests/test_ralph_state.py` - Add integration tests for branch base correctness, merge/remove failure handling, and retry cleanliness. (sources: reviewer-general, reviewer-second-opinion)
- Add a `ralph worktree list/status` operator command for debugging active/stale worktrees. (source: reviewer-second-opinion)
- Add stale-worktree age tracking + optional automatic cleanup policy. (source: reviewer-second-opinion)
- Document manual recovery steps for merge-conflict worktrees (`git worktree list`, resolve, merge, remove). (source: reviewer-second-opinion)
- Consider dispatch-specific keep-worktree/preflight options (capability and environment checks). (source: reviewer-second-opinion)

## Summary Statistics
- Critical: 3
- Major: 3
- Minor: 4
- Warnings: 3
- Suggestions: 5
