# Research: pt-0v53

## Status
Research completed. Comprehensive context gathered from project knowledge base and codebase.

## Rationale
Research was performed because:
1. This is a foundational ticket for the Ralph background interactive shell feature
2. It depends on worktree lifecycle management which needs careful design
3. Related topics (seed, plan, spike) provide critical context
4. The existing Ralph codebase has partial implementation that must be understood

## Context Reviewed

### Ticket Details (`tk show pt-0v53`)
- **Title**: Add per-ticket worktree lifecycle for dispatch runs
- **Type**: Task
- **Priority**: 2
- **Status**: open
- **Dependencies**: pt-6d99 [closed], pt-9yjn [open] (blocking)
- **External Ref**: seed-add-ralph-loop-background-interactive

### Key Requirements
- Worktree is created before dispatch starts for a ticket
- Dispatch runner executes with worktree as cwd
- Success path: merge and close worktree
- Failure path: safe cleanup
- Maintain compatibility with existing Ralph worktree options

### Knowledge Base Topics

#### 1. Seed: seed-add-ralph-loop-background-interactive
**Vision**: Ralph should support a mode where every ticket is implemented in a fresh interactive Pi process running autonomously in the background.

**Core Features**:
- Fresh context per ticket (new Pi session)
- Background autonomy with dispatch/background mode
- Live observability on demand (user can attach)
- Parallel workers with dependency/component safeguards
- State continuity with progress.md and AGENTS.md

**MVP Scope**:
- Add Ralph execution backend for per-ticket background interactive shell sessions
- Run `pi /tf <ticket-id> --auto` per ticket with fresh process isolation
- Wire session lifecycle into Ralph progress updates
- Support configurable parallel worker count

#### 2. Plan: plan-ralph-background-interactive-shell
**Status**: Approved (2026-02-13)

**Key Decisions**:
- Use `interactive_shell` dispatch/background mode as new default
- Worktree per ticket: create on start, merge/close on close
- Session exit = authoritative completion signal
- `--dispatch` flag as default, `--no-interactive-shell` for fallback

**Phases**:
1. **Foundation**: dispatch backend, worktree management, wire into loop
2. **Parallel Support**: concurrent sessions with component/dependency safety
3. **Observability**: user attachment commands
4. **Reliability**: timeout handling, cleanup logic

#### 3. Spike: spike-interactive-shell-execution
**Research Findings**:
- Current Ralph uses `pi -p` (batch/non-interactive)
- Proposal: Use `interactive_shell` with dispatch mode
- Completion detection via dispatch notification (triggerTurn)
- Benefits: simpler than worktrees, faster (no git ops), fresh context guaranteed

**Open Questions Addressed**:
- Q: How does Ralph know when `pi /tf --auto` is done?
  - A: Use dispatch mode with `triggerTurn` notification
- Q: Session lifecycle differences?
  - A: Non-blocking, monitored vs blocking subprocess

### Codebase Analysis

#### Current Ralph Implementation (`tf/ralph.py`)
**Execution Backend Support**:
- Config: `executionBackend`: "dispatch" (default) or "subprocess"
- CLI flags: `--dispatch` (default), `--no-interactive-shell`
- Interactive shell config: `interactiveShell.enabled: true` (default)

**Existing Worktree System**:
- `parallelWorktreesDir`: ".tf/ralph/worktrees"
- Used for parallel mode with component tags
- Worktrees created at lines ~2193-2264
- `keep_worktrees` option for retention

**Pending Implementation**:
- Line 582-585: Dispatch backend noted as "pending pt-9yjn implementation"
- Line 589: TODO comment for actual dispatch execution
- Currently falls back to subprocess even when dispatch is selected

**Key Functions**:
- `run_ticket()`: Main ticket execution (line ~564)
- Worktree creation/management around line 2193+
- Command building around line 393-416

## Technical Design Considerations

### Worktree Lifecycle Flow
```
1. Ticket Start
   └── Create worktree from main repo
   └── Store worktree path

2. Dispatch Execution
   └── interactive_shell(command: 'pi /tf {ticket} --auto', cwd: worktree_dir)
   └── Session runs in worktree context

3. Success Path
   └── Merge worktree changes to main
   └── Close (remove) worktree
   └── Update progress

4. Failure Path
   └── Safe cleanup (remove worktree without merge)
   └── Log failure details
```

### Integration Points
1. **Config system**: Already supports `executionBackend` setting
2. **CLI flags**: Already supports `--dispatch` and `--no-interactive-shell`
3. **Worktree directory**: Already configured via `parallelWorktreesDir`
4. **Progress tracking**: Existing `.tf/ralph/progress.md` system
5. **Blocking ticket**: pt-9yjn implements the actual dispatch launcher

### Compatibility Requirements
- Must work with existing parallel worktree options
- Must preserve dependency ordering (pt-6d99 defines contract)
- Must not break subprocess fallback mode
- Progress and lessons extraction must continue working

## Sources

1. **Ticket**: `tk show pt-0v53`
2. **Seed**: `.tf/knowledge/topics/seed-add-ralph-loop-background-interactive/`
   - seed.md, overview.md, mvp-scope.md, constraints.md, assumptions.md
3. **Plan**: `.tf/knowledge/topics/plan-ralph-background-interactive-shell/plan.md`
4. **Spike**: `.tf/knowledge/topics/spike-interactive-shell-execution/spike.md`
5. **Code**: `tf/ralph.py` (execution backend config, worktree handling)
6. **Dependencies**: pt-6d99 [closed] - dispatch contract, pt-9yjn [open] - dispatch launcher

## Implementation Notes

This ticket focuses specifically on the **worktree lifecycle** - creating, managing, and cleaning up worktrees for dispatch runs. The actual dispatch execution logic is handled by pt-9yjn.

**Key work areas**:
1. Worktree creation on ticket start (reuse existing parallel worktree logic)
2. Passing worktree directory to dispatch runner
3. Merge logic on successful completion
4. Cleanup logic on failure
5. Integration with existing `keep_worktrees` option

**Related worktree code locations**:
- `tf/ralph.py:2193-2206` - Worktree directory setup
- `tf/ralph.py:2262-2264` - Dry run logging with worktree context
- Search for `parallelWorktreesDir` for all references
