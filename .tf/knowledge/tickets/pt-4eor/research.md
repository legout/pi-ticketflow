# Research: pt-4eor

## Status
Research completed. Internal analysis of codebase and planning documents.

## Rationale
This ticket requires integrating the dispatch backend into the serial Ralph loop (`tf ralph start` with `--parallel 1` or default). Currently, the dispatch backend is only fully implemented for:
- `tf ralph run` (single ticket dispatch-and-return)
- `tf ralph start --parallel N` (parallel batch dispatch with polling)

The serial loop in `ralph_start()` still uses the legacy `run_ticket()` subprocess approach even when `execution_backend == "dispatch"`.

## Context Reviewed

### Ticket Details (pt-4eor)
- **Task**: Wire dispatch runner into serial `tf ralph run/start` execution and keep progress/lessons updates intact
- **Acceptance Criteria**:
  1. Serial loop uses dispatch backend by default
  2. Progress entries and issue summaries are still written as before
  3. Lessons extraction still appends to `.tf/ralph/AGENTS.md`

### Planning Documents

#### Seed: seed-add-ralph-loop-background-interactive
Vision: Ralph should support a mode where every ticket is implemented in a fresh interactive Pi process running autonomously in the background.

Key features:
1. Fresh context per ticket (one new Pi session per implementation)
2. Background autonomy (loop continues without manual input)
3. Live observability on demand (attach to any running session)
4. State continuity (keep `.tf/ralph/progress.md` and `.tf/ralph/AGENTS.md` semantics unchanged)

#### Spike: spike-interactive-shell-execution
Research on executing Ralph using background `interactive_shell` sessions.

Key findings:
- Use dispatch mode with `triggerTurn` notification for completion detection
- Session exit is the completion signal
- Multiple `interactive_shell` background sessions can run concurrently
- Progress file still updated after each ticket
- Lessons extracted from session output

#### Backlog Dependencies
```
pt-6d99 (Define dispatch-default contract)
  → pt-0v53 (Per-ticket worktree lifecycle)
    → pt-9yjn (run_ticket_dispatch launcher)
      → pt-7jzy (Handle dispatch completion)
        → pt-699h (Parallel dispatch scheduling)
          → pt-8qk8 (Orphaned session recovery)
            → pt-uu03 (Manual validation)
              → pt-4eor (THIS TICKET: Serial loop integration)
                → pt-zmah (Session observability)
```

### Code Analysis

#### Current State in `tf/ralph.py`

**`ralph_run()` (single ticket)** - Line ~2068:
- Already uses `run_ticket_dispatch()` when `execution_backend == "dispatch"`
- Returns immediately after launch with "DISPATCHED" status
- Does NOT wait for completion (designed for fire-and-forget)

**`ralph_start()` serial mode** - Line ~2600+:
- Calls `run_ticket()` which uses `pi -p` subprocess (blocking)
- Does NOT use dispatch backend even when configured
- Updates progress via `update_state()` after completion

**`ralph_start()` parallel mode** - Line ~2800+:
- Uses `run_ticket_dispatch()` for each ticket
- Polls completion with `poll_dispatch_status()`
- Updates progress after each ticket completes

#### Key Functions

```python
# Launch dispatch session (already implemented)
run_ticket_dispatch(
    ticket, workflow, flags, dry_run,
    cwd=worktree_cwd, ralph_dir=ralph_dir, ...
) → DispatchResult

# Poll for completion (already implemented)
poll_dispatch_status(pid) → (is_running, return_code)

# Update progress and lessons (already implemented)
update_state(ralph_dir, project_root, ticket, status, error_msg)
```

#### State Update Flow (Current)
1. `update_state()` reads `close-summary.md` from artifact directory
2. Extracts: summary, commit hash, issue counts (Critical/Major/Minor), lessons
3. Appends entry to `progress.md`
4. Appends lesson block to `AGENTS.md`

### Implementation Strategy

The serial loop needs to:
1. Use `run_ticket_dispatch()` instead of `run_ticket()` when `execution_backend == "dispatch"`
2. Poll for completion using `poll_dispatch_status()` (similar to parallel mode)
3. Handle worktree lifecycle (create → launch → poll → merge/cleanup)
4. Call `update_state()` after completion to write progress and lessons

Key code sections to modify:
- Serial execution loop in `ralph_start()` around line 2600-2750
- Replace the `run_ticket()` call with dispatch launch + poll pattern
- Keep existing `update_state()` call after completion

### State Preservation Requirements

From the ticket constraints:
- Ralph state files (`progress.md`, `AGENTS.md`) are core contracts and must remain stable
- Execution transport changes should not break status or lesson extraction behavior

The existing `update_state()` function already handles this correctly:
- Reads from `artifact_dir/close-summary.md` for summary/commit/lessons
- Reads from `artifact_dir/review.md` for issue counts
- Appends to `progress.md` with consistent format
- Appends lessons to `AGENTS.md`

## Sources
- `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/seed.md`
- `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/backlog.md`
- `.tf/knowledge/topics/spike-interactive-shell-execution/spike.md`
- `tf/ralph.py` (comprehensive code review)
- `tk show pt-4eor` (ticket details)
- `tk show pt-uu03` (validation ticket for context)
