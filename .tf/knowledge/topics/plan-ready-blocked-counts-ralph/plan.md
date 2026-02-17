---
id: plan-ready-blocked-counts-ralph
status: revised
last_updated: 2026-02-10
---

# Plan: Show ready/blocked ticket counts in Ralph progress + logs

## Summary

Improve Ralph run observability by surfacing queue state in a way that answers “what can run now vs what is waiting on dependencies?”. Specifically, replace/augment the current progress indicator (e.g. `[1/5]`) with explicit **ready** and **blocked** counts, and include the same counts in normal logging at ticket start and finish.

This should be derived from Ralph’s in-memory view of the dependency graph / scheduler state to avoid expensive recomputation, and must behave correctly in both TTY and non-TTY environments.

## Inputs / Related Topics

- Root Seed: [seed-show-ready-and-blocked-ticket-count](topics/seed-show-ready-and-blocked-ticket-count/seed.md)
- Session: seed-show-ready-and-blocked-ticket-count@2026-02-10T11-49-49Z
- Related Spikes:
  - (none yet)

## Requirements

- Progress output (progress bar / single-line progress) shows at least:
  - `ready` count
  - `blocked` count
  - (optional but recommended) `done` and/or `total`
- **Display format**: Use `R:3 B:2 (done 1/6)` format (or similar variant) that is both human-readable and machine-parseable.
- In normal logging mode, log the current counts when:
  - starting a ticket
  - finishing a ticket (success or failure)
- Counts update correctly as tickets transition blocked → ready (dependency satisfaction).
- Output remains readable in non-TTY mode (no animated control characters).

**State definitions** (derived from consultant recommendation):
- `ready`: tickets that are runnable but not currently running
- `blocked`: tickets that cannot run due to unmet dependencies (deps-only for MVP)
- `running`: ticket currently being processed
- `done`: tickets completed (success or failure)

## Constraints

- Avoid expensive recomputation (do not repeatedly re-list/reload all tickets just to compute counts).
- Do not break existing `tk ralph` output contracts for scripts (prefer additive changes or format behind an explicit flag).
- Ensure consistent semantics for “ready/blocked/running/done” and document them.

## Assumptions

- Ralph has (or can derive) a stable notion of ticket states: ready, blocked, running, done.
- The dependency graph is available in memory during a run.
- `blocked` definition for MVP is deps-only; other blocking reasons (filters, component locks, failures) are out of scope.

## Risks & Gaps

- ~~**Ambiguous definition of “blocked”**: tickets may be blocked for reasons beyond deps (filters, component locking, failures).~~ → **Resolved**: MVP uses deps-only definition; other reasons out of scope.
- ~~**Current ticket accounting**: whether the running ticket is included in ready/done can cause off-by-one confusion.~~ → **Resolved**: Running ticket excluded from ready; tracked separately.
- **Output compatibility**: changing a string used by tests or scripts could break users. Mitigation: gate formatting changes behind a flag, or keep old format as fallback.
- **Testing complexity**: extracting scheduler logic may be difficult. Mitigation: computation helper will be in dedicated `queue_state.py` module for unit testing.

## Work Plan (phases / tickets)

1. **Baseline the current progress + logging path**
   - Locate where `[x/y]` (or equivalent) is computed and printed.
   - Identify the authoritative in-memory structures that represent:
     - pending candidates
     - runnable queue
     - dependency graph / unmet deps
     - completed set

2. **Define queue state semantics + formatting**
   - Define what counts as `ready`, `blocked`, `running`, `done`.
   - Decide display format for progress bar and for log lines.
   - Ensure format works in TTY and non-TTY.

3. **Implement count computation helper**
   - Implement a single function that returns a snapshot:
     - ready_count
     - blocked_count
     - running_count (optional)
     - done_count / total_count (optional)
   - Ensure computation is O(n) over known in-memory ticket list and does not re-query external systems.
   - **Extract from ralph.py**: move the computation function into a dedicated helper module (e.g., `ralph/queue_state.py`) to enable unit testing without importing the full scheduler.

4. **Integrate into progress display**
   - Replace/augment progress indicator to include ready/blocked counts.
   - Ensure progress display updates whenever scheduler state changes.

5. **Integrate into normal logging**
   - Add log lines at ticket start and finish that include the counts.
   - Ensure errors still print clearly.

6. **Tests + docs**
   - **Unit tests** for `queue_state.py` helper (ready/blocked/running/done invariants).
   - **Integration tests** for log output (stdout) and progress display.
   - Add snapshot-style tests for formatting where appropriate.
   - Update CLI help/docs if there is a user-facing flag or if output meaning changes.

## Acceptance Criteria

- [ ] Progress output clearly displays ready + blocked counts during a Ralph run.
- [ ] Normal logging prints ready/blocked counts on ticket start and finish.
- [ ] Counts are consistent with scheduler state and update when dependencies are satisfied.
- [ ] Non-TTY output is readable and contains the same information (no animated control chars).
- [ ] Unit tests cover queue state computation invariants (ready/blocked/running/done).
- [ ] Integration tests verify log output and progress formatting.

## Open Questions

- Should output format changes be gated behind a flag to preserve backwards compatibility for scripts/tests?

---

## Consultant Notes (Metis)

- 2026-02-10: Drafted plan from seed; key risk is semantic ambiguity around "blocked". Recommend defining invariants explicitly and gating format changes behind a flag if output stability matters.
- 2026-02-10: **Consultation findings**:
  - **Gap identified**: Unclear whether counts include already-running tickets. Resolution: explicitly define `ready` = runnable but not currently running; `running` = in-progress; `done` = completed (success or failure). Update work plan to include definition work.
  - **Gap identified**: Format string not specified for non-TTY. Resolution: recommend `R:3 B:2 (done 1/6)` format, which is machine-parseable and human-readable.
  - **Risk**: Testing may be difficult if scheduler logic is tangled. Resolution: extract computation helper into separate module (added to work plan ticket 3).
  - **Suggestion**: Add test coverage expectations (unit for helper, integration for stdout/progress) to acceptance criteria.

## Reviewer Notes (Momus)

- 2026-02-10: (pending)

---

## Revision Notes

- 2026-02-10: **Applied consultant feedback**:
  - Added display format specification (`R:3 B:2 (done 1/6)`) to Requirements.
  - Added explicit state definitions (ready/blocked/running/done) to Requirements.
  - Updated Assumptions to clarify deps-only scope for `blocked`.
  - Resolved key risks in Risks & Gaps section (marked as resolved with decisions).
  - Cleaned up Open Questions to focus on remaining flag/backwards-compat question.
  - Status changed from `consulted` → `revised`.
