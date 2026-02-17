---
id: plan-ralph-background-interactive-shell
status: approved
last_updated: 2026-02-13
---

# Plan: Ralph Loop with Background Interactive Shell Execution

## Summary

Implement a Ralph execution mode that runs each ticket implementation in a fresh **background interactive shell** (`pi /tf ... --auto`) using Pi's `interactive_shell` dispatch/background mode. This provides guaranteed fresh context per ticket, parallel execution capability, and live observability on demand while maintaining autonomous throughput.

## Inputs / Related Topics

- Root Seed: [seed-add-ralph-loop-background-interactive](topics/seed-add-ralph-loop-background-interactive/seed.md)
- Session: seed-add-ralph-loop-background-interactive@2026-02-13T15-28-56Z
- Related Spikes:
  - [spike-interactive-shell-execution](topics/spike-interactive-shell-execution/spike.md)

## Requirements

1. **Dispatch mode as default**: Use `interactive_shell` dispatch/background mode as the new default execution path
2. **Worktree per ticket**: Create git worktree on ticket start, merge and close on ticket close
3. **Fresh context**: Each dispatched interactive shell has its own Pi session and context
4. **Completion detection**: Detect when a background ticket session completes (via dispatch notification)
5. **Parallel coordination**: Support running multiple background sessions concurrently with component/dependency safety
6. **Progress continuity**: Update `.tf/ralph/progress.md` and extract lessons to `.tf/ralph/AGENTS.md` after each ticket
7. **User attachment**: Allow users to attach to running sessions for live observation

## Constraints

- Must preserve existing Ralph safety semantics (dependency ordering, component isolation)
- Must not require user interaction for autonomous runs
- Must guarantee cleanup/termination of background sessions to avoid resource leaks
- Must maintain compatibility with existing `tf ralph status`, progress files, and lessons flow
- Implementation should be incremental (MVP first, then enhancements)

## Assumptions

- `interactive_shell` dispatch/background mode is reliable for long-running Pi ticket implementations
- Each dispatched shell has its own Pi session and context - this is the core goal
- Git worktrees can be created on-the-fly per ticket and cleaned up after merge
- Ralph's existing dependency/component gating logic can be reused for parallel scheduling
- Progress and lessons should remain file-based so loop state survives process/context resets

## Risks & Gaps

1. **Completion signal uncertainty**: Not fully verified if `pi /tf --auto` exits automatically on workflow completion
2. **Session timeout handling**: Need to implement timeout detection and session killing for stuck sessions
3. **Orphaned sessions**: Ralph restart may leave orphaned background sessions
4. **Output capture**: Need to capture and store session output for debugging/lessons extraction

## Work Plan (phases / tickets)

### Phase 1: Foundation (MVP)

1. **Add dispatch execution backend**
   - Create new function `run_ticket_dispatch()` in `tf/ralph.py`
   - Use `interactive_shell` dispatch mode with `pi /tf <ticket> --auto`
   - Each dispatch gets its own Pi session (fresh context guaranteed)
   - Handle completion notification from dispatch

2. **Add --dispatch flag (new default)**
   - Add `--dispatch` flag to `tf ralph run/start` (default: enabled)
   - Add `--no-interactive-shell` flag as fallback to old implementation
   - Default to dispatch mode for new runs

3. **Add worktree management per ticket**
   - Create worktree on ticket start
   - Run dispatch in worktree directory
   - Merge changes and close worktree on ticket close
   - Handle cleanup on failure

4. **Wire into Ralph loop**
   - Replace `run_ticket()` with `run_ticket_dispatch()` when dispatch enabled
   - Update progress tracking for new execution model

### Phase 2: Parallel Support

5. **Add parallel coordination for dispatch sessions**
   - Track multiple concurrent session IDs
   - Use existing component tags for dependency safety
   - Wait for session completions before starting dependent tickets

6. **Implement session monitoring**
   - Poll or wait for session completion
   - Handle mixed success/failure states

### Phase 3: Observability

7. **Add user attachment commands**
   - Log session IDs for user reference
   - Document how to attach to running sessions

8. **Improve output capture**
   - Capture session output to files
   - Store for debugging and lessons extraction

### Phase 4: Reliability

9. **Add timeout handling**
   - Detect stuck/hanging sessions
   - Implement session killing after timeout

10. **Add cleanup logic**
    - Handle orphaned sessions on Ralph restart
    - Auto-cleanup finished sessions

## Acceptance Criteria

- [ ] `tf ralph run <ticket> --dispatch` executes ticket in dispatched interactive shell
- [ ] Each dispatch has its own Pi session (fresh context verified)
- [ ] Worktree created on ticket start, merged and closed on ticket close
- [ ] Completion is detected and progress is updated
- [ ] Lessons are extracted to `.tf/ralph/AGENTS.md` after each ticket
- [ ] `tf ralph start --parallel 3` runs 3 tickets concurrently (dispatch mode)
- [ ] User can attach to running sessions to observe progress
- [ ] `--no-interactive-shell` falls back to old implementation
- [ ] Stuck sessions are killed after timeout
- [ ] Progress files remain compatible with existing tools

## Decisions / Resolved Questions

1. **`pi /tf ... --auto` exit behavior**: Treat *session exit* as authoritative completion signal. If a session remains idle after workflow completion, send graceful EOF (`Ctrl+D`) then kill on timeout.
2. **Completion pattern**: Prefer dispatch/session lifecycle completion over fragile text parsing. Promise sigils are optional diagnostics, not the primary completion trigger.
3. **Recovery on restart**: On Ralph startup, detect orphaned sessions for this run, mark stale ones, and kill/cleanup before scheduling new tickets.
4. **Finished session retention**: Keep completed session metadata/log pointers briefly for debugging (TTL), then auto-cleanup.

---

## Consultant Notes (Metis)

- 2026-02-13: Plan drafted from seed + spike research. Core approach is sound - using dispatch mode with notification. Main uncertainty is auto-exit behavior.

### Gap Detection

**Missing integration details:**
- Plan modifies `tf/ralph.py` but doesn't address how new backend coexists with existing parallel worktree system
- No mention of whether `/tf` prompt needs modifications for interactive shell dispatch

**Session state management gaps:**
- How does Ralph track running sessions? Need new state file or extend existing?
- What happens when background session fails unexpectedly (not just timeout)?

**Backward compatibility:**
- Plan says "default to existing" but doesn't specify how users switch between backends
- Should new flag be `--dispatch` or `--interactive-shell`?

**MVP scope unclear:**
- Phases described but which tickets are MVP vs enhancement not clearly marked
- Phase 1 has 3 tickets - is that the full MVP or should it be smaller?

**Testing gap:**
- No mention of how this will be tested (unit? integration?)

### Required Changes

1. ~~Clarify backend coexistence~~: Addressed - dispatch mode replaces worktree mode, worktree per ticket
2. ~~Add session state requirements~~: Addressed - each dispatch has its own session
3. ~~Define flag name~~: Addressed - `--dispatch` default, `--no-interactive-shell` fallback
4. ~~Split Phase 1~~: Addressed - will split into small tickets during backlog generation
5. ~~Add testing notes~~: Addressed - manual testing

**Status after revision**: All gaps addressed

## Reviewer Notes (Momus)

- 2026-02-13: PASS
  - Blockers:
    - None
  - Required changes:
    - None (completion/recovery decisions are now explicit and testable)
  - Review summary:
    - Requirements are complete and bounded.
    - Constraints and risks are captured with concrete mitigations.
    - Work sequencing is feasible (foundation → parallel → observability → reliability).
    - Acceptance criteria are implementation-oriented and verifiable via manual tests.
