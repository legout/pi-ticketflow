# Review: pt-4eor

## Critical (must fix)
- `tf/ralph.py:157-159,959,2848-2872` - Dispatch child PIDs are registered but not reliably unregistered in all serial dispatch completion paths, which can leave stale PIDs in `_dispatch_child_pids` and risk terminating unrelated process groups on later signal handling. _(source: reviewer-general)_

## Major (should fix)
- `tf/ralph.py:976-987,2824-2872` - Serial dispatch path may leave `dispatch-sessions.json` entries as `running` because terminal status updates are missing/incomplete compared with parallel handling. _(source: reviewer-general)_
- `tf/ralph.py:2788-2794` - Worktree leak risk on dispatch launch failure; cleanup should occur before returning failure. _(source: reviewer-second-opinion)_

## Minor (nice to fix)
- `tf/ralph.py:2841-2843,2965-2974` - Launch-failure diagnostics can be collapsed into generic `pi -p failed` messaging, losing actionable context for retries. _(source: reviewer-general)_
- `tf/ralph.py:2797` - Keep `update_dispatch_tracking_status` import at module level for consistency/readability. _(source: reviewer-second-opinion)_
- `tf/ralph.py:2839-2850` - On timeout restart path (`ticket_rc == -1` and retry), ensure current worktree is always cleaned before continuing to avoid accumulation across retries. _(source: reviewer-second-opinion)_

## Warnings (follow-up ticket)
- `.tf/knowledge/tickets/pt-4eor/implementation.md:22-35` - Reviewer noted test-confidence gap from an apparent mismatch in recorded verification details; re-validate artifact/test reporting consistency. _(source: reviewer-general)_

## Suggestions (follow-up ticket)
- `tf/ralph.py` - Add focused serial-dispatch lifecycle tests that assert (1) child PID unregistration and (2) session status transitions to terminal states. _(source: reviewer-general)_
- `tf/ralph.py` - Consider startup cleanup for stale/orphaned worktrees as a defensive complement to session recovery. _(source: reviewer-second-opinion)_

## Summary Statistics
- Critical: 1
- Major: 2
- Minor: 3
- Warnings: 1
- Suggestions: 2
