---
id: plan-add-ralph-loop-that-runs-in-a-background
status: consulted
last_updated: 2026-02-13
---

# Plan: Add Ralph loop with background interactive shell and parallel ticket implementation

## Summary

Add a Ralph execution mode that runs ticket implementation through background `interactive_shell` sessions while preserving observability and operator control. The goal is to support non-blocking ticket execution, optional live attach/takeover, and safer long-running runs without losing command output.

Extend Ralph to support parallel ticket implementation based on readiness and component-tag constraints, so multiple safe tickets can run concurrently when configured. The design should remain backward-compatible with the current sequential flow and preserve current quality-gate and review behavior.

## Inputs / Related Topics

- Root Seed: [seed-add-ralph-loop-background-interactive](topics/seed-add-ralph-loop-background-interactive/seed.md)
- Session: seed-add-ralph-loop-background-interactive@2026-02-13T15-28-56Z
- Related Spikes:
  - [spike-interactive-shell-execution](topics/spike-interactive-shell-execution/spike.md)

## Requirements

- Add a Ralph execution path that launches ticket implementation via `interactive_shell` in background/dispatch mode.
- Ensure each ticket execution can be monitored, re-attached, terminated, and resumed from Ralph state.
- Support parallel execution of ready tickets when `ralph.parallelWorkers > 1`.
- Respect dependency constraints (`tk dep`) and component-tag safety (`component:*`) in parallel scheduling.
- Preserve current Implement → Review → Fix → Close behavior per ticket.
- Keep sequential behavior unchanged when `parallelWorkers = 1`.
- Persist session metadata (session ID, ticket ID, worker slot, start/end timestamps, final outcome) in Ralph artifacts.
- Enforce timeout/retry policy compatibility with existing Ralph iteration controls.
- Ensure deterministic scheduling policy (FIFO by ready time, with stable tie-breaker) for reproducibility.

## Constraints

- Must not regress current Ralph defaults and CLI ergonomics.
- Must avoid spawning parallel work on unsafe/untagged tickets unless explicitly configured.
- Must avoid orphaned background processes/sessions after interruption or failure.
- Must preserve compatibility with `.tf/ralph` progress and state artifacts.
- Must isolate per-ticket working directories/artifacts so parallel workers do not overwrite each other.

## Assumptions

- `interactive_shell` supports stable background dispatch sessions and completion notifications.
- Existing ticket selection logic can provide a ready-set for parallel scheduling.
- Component tags are sufficiently present to enable safe parallelization in typical projects.
- Ticket execution is idempotent enough that retries do not corrupt ticket artifacts.

## Risks & Gaps

- Ambiguity around ownership of background session lifecycle (Ralph vs interactive_shell tool abstraction).
- Race conditions in scheduler updates when multiple tickets complete near-simultaneously.
- Incomplete component tagging may reduce usable parallelism.
- Failure-handling behavior for partially completed parallel batches is underspecified.
- Potential artifact collisions if shared files are written from multiple workers.

## Work Plan (phases / tickets)

1. **Execution model specification**
   - Define worker/ticket states (`queued`, `running`, `completed`, `failed`, `cancelled`, `timed_out`).
   - Define lifecycle ownership between Ralph and interactive_shell sessions.
2. **Session runner abstraction**
   - Implement per-ticket background execution wrapper with start/query/kill and outcome mapping.
   - Record structured session metadata in Ralph run state.
3. **Parallel scheduler**
   - Implement dependency-aware ready queue.
   - Enforce component-tag policy and worker slot limit.
   - Use deterministic tie-breaking.
4. **Ralph loop integration**
   - Integrate scheduler + runner while preserving existing sequential path.
   - Ensure cancellation/interrupt drains active workers safely.
5. **Observability and artifact safety**
   - Extend progress/log output with worker/session information.
   - Add per-worker artifact isolation and merge-safe result recording.
6. **Testing and docs**
   - Unit tests for scheduler correctness and state transitions.
   - Integration tests for background sessions, failures, and shutdown.
   - Docs/help updates for new flags/config and operational caveats.

## Acceptance Criteria

- [ ] Ralph can run ticket implementation in background `interactive_shell` mode without blocking the main loop.
- [ ] Parallel execution works for eligible ready tickets when configured and never violates dependencies.
- [ ] Component-tag safety rules are enforced in parallel mode according to config.
- [ ] Session metadata is captured for every ticket run (session ID, worker slot, outcome, timestamps).
- [ ] Ticket artifacts and close flow remain correct for each completed ticket under parallel load.
- [ ] Interruptions and failures do not leave unmanaged background sessions.
- [ ] Logs/progress provide enough detail to inspect and debug multi-worker runs.
- [ ] Tests cover sequential compatibility, scheduler edge cases, timeout/retry behavior, and shutdown handling.

## Open Questions

- Should background mode be defaulted automatically for `parallelWorkers > 1`, or gated behind an explicit CLI/config flag?
- What is the minimum required behavior when component tags are missing (strict block vs best-effort fallback)?
- How should partial failure in one worker influence other active workers (continue vs coordinated stop)?

---

## Consultant Notes (Metis)

- 2026-02-13: Drafted initial plan from request + active planning session context.
- 2026-02-13: Consultation found missing specifics on state model, metadata persistence, deterministic scheduling, and artifact isolation. Added explicit requirements, constraints, and test-focused acceptance criteria.

## Reviewer Notes (Momus)

- 2026-02-13: (pending)
