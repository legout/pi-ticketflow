# Research: pt-6d99

## Status
Research completed. Internal planning documentation review complete.

## Rationale
This is a contract definition ticket - the work involves codifying execution behavior flags rather than external research. The context comes from internal planning documents.

## Context Reviewed

### Ticket Requirements
- Define and codify dispatch-mode defaults and fallback flags for Ralph execution
- `--dispatch` is defaulted for `tf ralph run` and `tf ralph start`
- `--no-interactive-shell` cleanly routes to legacy subprocess backend
- Help/usage text reflects the new default and fallback

### Key Planning Documents

#### Seed: seed-add-ralph-loop-background-interactive
The seed describes a vision where Ralph supports background interactive Pi processes via `interactive_shell` tool instead of subprocess-based `pi -p` execution:
- Fresh context per ticket (new Pi session per implementation)
- Background autonomy (loop continues without manual input)
- Live observability on demand (can attach to running sessions)
- Parallel workers with dependency/component safeguards

#### Backlog Dependencies
This ticket (pt-6d99) is the first in a chain:
1. **pt-6d99** (this ticket) - Define dispatch-default execution contract
2. pt-0v53 - Add per-ticket worktree lifecycle for dispatch runs
3. pt-9yjn - Implement run_ticket_dispatch launcher for Ralph
4. pt-7jzy - Handle dispatch completion and graceful session termination
5. pt-699h - Implement parallel dispatch scheduling with component safety
6. etc.

### Current Code Analysis (tf/ralph.py)

Current execution uses `subprocess.Popen` to run `pi -p "/tf <ticket>"`:
- `run_ticket()` function handles the subprocess execution
- Serial mode: direct subprocess with timeout/restart support
- Parallel mode: git worktrees + subprocess per ticket

The new dispatch mode will use `interactive_shell` tool with `mode="dispatch"` for headless background execution.

### Execution Contract Design

#### Flag Semantics
- `--dispatch` (default): Use `interactive_shell` tool in dispatch mode for headless background execution
- `--no-interactive-shell`: Use legacy subprocess backend (`pi -p` via `subprocess.Popen`)

#### Config Integration
New config options in `.tf/ralph/config.json`:
```json
{
  "executionBackend": "dispatch",
  "interactiveShell": {
    "enabled": true,
    "mode": "dispatch"
  }
}
```

#### Backward Compatibility
- Existing configs without these settings default to new dispatch behavior
- `--no-interactive-shell` provides explicit opt-out
- Environment variable `RALPH_NO_INTERACTIVE_SHELL=1` for global override

## Sources
- `.tickets/pt-6d99.md` - Ticket definition
- `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/seed.md` - Feature vision
- `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/backlog.md` - Implementation roadmap
- `tf/ralph.py` - Current Ralph implementation (lines 1-2306)
- `tf/cli.py` - CLI command definitions
