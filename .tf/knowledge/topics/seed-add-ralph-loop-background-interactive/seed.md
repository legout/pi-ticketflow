# Seed: Ralph loop with background interactive shells + parallel ticket execution

## Vision
Ralph should support a mode where every ticket is implemented in a fresh interactive Pi process that can run autonomously in the background, while still being inspectable live when needed.

## Core Concept
Replace (or add alongside) the current per-ticket `pi -p /tf ...` execution path with `interactive_shell` background dispatch sessions that run `pi /tf <ticket-id> --auto`. Each ticket gets its own isolated process/context. Ralph orchestrates multiple concurrent sessions (subject to component/dependency safety), tracks completion, updates progress, and extracts lessons after each ticket finishes.

## Key Features
1. **Fresh context per ticket**: one new Pi session per implementation, no context bleed.
2. **Background autonomy**: loop continues without manual input using dispatch/background mode.
3. **Live observability on demand**: user can attach to any running session to watch/intervene.
4. **Parallel workers**: run multiple ticket sessions concurrently with dependency/component safeguards.
5. **State continuity**: keep `.tf/ralph/progress.md` and `.tf/ralph/AGENTS.md` semantics unchanged.

## Open Questions
- Should this be a new command (e.g. `tf ralph start --interactive-shell`) or the default backend?
- What is the exact completion signal for a background interactive Pi ticket session?
- How should Ralph recover from orphaned/stuck background sessions on restart?
- Should finished sessions be auto-cleaned immediately or retained briefly for debugging?
