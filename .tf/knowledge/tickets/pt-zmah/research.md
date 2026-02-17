# Research: pt-zmah

## Status
Research completed - background context gathered from related tickets, seed, spike, and codebase.

## Rationale
Research needed to understand:
1. The dispatch backend architecture already implemented in pt-4eor
2. Current session tracking mechanisms in Ralph
3. What observability features are missing for dispatch sessions

## Context Reviewed

### Ticket Details (pt-zmah)
- **Task**: Improve observability by logging session IDs, attach instructions, and output artifact pointers
- **Acceptance Criteria**:
  - [ ] Ralph logs session ID for each dispatched ticket
  - [ ] Logs include how to attach/watch a running session
  - [ ] Output capture paths are recorded for completed/failed tickets
- **Constraints**: Keep default logs concise; avoid noisy output explosion

### Related Ticket (pt-4eor - CLOSED)
Already implemented the dispatch backend integration into serial Ralph loop:
- Serial loop uses dispatch backend by default
- Progress entries and issue summaries still written
- Lessons extraction still appends to `.tf/ralph/AGENTS.md`

### Seed: seed-add-ralph-loop-background-interactive
Vision: Ralph supports background interactive Pi processes that run autonomously while being inspectable live.

Key features:
1. Fresh context per ticket (one new Pi session per implementation)
2. Background autonomy using dispatch/background mode
3. Live observability on demand (user can attach to running session)
4. Parallel workers with dependency/component safeguards
5. State continuity (progress.md and AGENTS.md semantics unchanged)

### Spike: spike-interactive-shell-execution
Research on executing Ralph with `interactive_shell` instead of `pi -p`:
- Uses dispatch mode with `triggerTurn` notification
- Session exit is the completion signal
- Multiple background sessions can run concurrently
- User can `interactive_shell({ sessionId: "xxx", attach: "xxx" })` to watch live

### Codebase Analysis

**Current Dispatch Implementation** (`tf/ralph.py`):
- `_allocate_dispatch_session_id()` generates UUIDs for sessions
- `run_ticket_dispatch()` function launches `pi -p "/tf {ticket} --auto"` via interactive_shell
- Session ID logged at dispatch: `log.info(f"Dispatching: pi -p "{cmd}" (session: {session_id})")`
- Session info stored in state: `update_state(ralph_dir, project_root, ticket, "DISPATCHED", f"session_id={dispatch_result.session_id}")`

**Current Gaps for Observability**:
1. Session ID is logged but not prominently displayed for users
2. No instructions on how to attach to a running session
3. Output paths are logged but not in a consistent, discoverable format
4. No summary at end showing how to access completed session artifacts

**Key Code Locations**:
- `tf/ralph.py:890-1003` - `run_ticket_dispatch()` function
- `tf/ralph.py:2417-2436` - Dispatch result handling with session_id logging
- `tf/ralph_completion.py` - Dispatch monitoring and graceful termination

## Implementation Approach

1. **Add session ID logging with attach instructions**:
   - After dispatch, log: `Session {session_id} started. Attach with: pi /attach {session_id}`
   
2. **Add output artifact path logging**:
   - Log output file path when `--pi-output=file` is used
   - Include session artifact directory path

3. **Add completion summary with artifact pointers**:
   - When ticket completes/fails, log paths to:
     - Session output log
     - Ticket artifacts (research.md, implementation.md, etc.)
     - How to re-attach if session still active

4. **Keep logs concise**:
   - Use single-line format for normal logs
   - Detailed paths only in verbose mode or on completion

## Sources
- `tk show pt-zmah` - Ticket details
- `tk show pt-4eor` - Related closed ticket
- `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/seed.md`
- `.tf/knowledge/topics/spike-interactive-shell-execution/spike.md`
- `tf/ralph.py` - Main Ralph implementation
- `tf/ralph_completion.py` - Dispatch completion handling
- `.tf/config/settings.json` - Ralph configuration
