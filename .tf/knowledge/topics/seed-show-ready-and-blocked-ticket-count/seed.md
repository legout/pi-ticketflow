# Seed: Show ready/blocked ticket counts in Ralph progress + logs

## Vision

When running the Ralph loop, operators should immediately understand *why* progress is slow: are there lots of tickets still ready to run, or are we mostly blocked waiting on dependencies?

## Core Concept

Track and surface two key queue metrics throughout a Ralph run:

- **Ready**: tickets that are runnable now
- **Blocked**: tickets that cannot run yet due to dependencies / ordering constraints

Show these metrics both in the progress bar display and in normal (non-progressbar) logging at key milestones.

## Key Features

1. **Progress bar shows ready vs blocked**: Replace/augment the current progress indicator (e.g. `[1/5]`) with explicit counts (ready/blocked, optionally plus done/total).
2. **Normal logging includes counts**: When starting a ticket and when finishing a ticket, log the current ready/blocked counts.
3. **Accurate during state changes**: Counts update as dependencies are satisfied and tickets transition from blocked → ready.

## Open Questions

- What is the exact definition of **blocked** in the Ralph loop?
  - strictly “has unmet dependencies” vs other reasons (filters, component locks, failures)
- What is the best display format?
  - `ready=3 blocked=2 done=1 total=6`
  - `R:3 B:2 (done 1/6)`
- Where should counts be computed from?
  - Ralph’s internal queue model vs shelling out to `tk` to recompute
- How should the counts treat the **currently running** ticket?
  - remove from ready immediately when started; add to done on completion
- Non-TTY behavior:
  - ensure logs remain readable and avoid animated control characters
