---
id: plan-increase-timeout-on-each-iteration-defau
status: draft
last_updated: 2026-02-10
---

# Plan: Increase timeout on each iteration (default +150000 ms)

## Summary

Some operations (e.g. ticket runs / retries / loop iterations) legitimately take longer on later attempts due to increased context, larger diffs, or additional review/fix steps. A fixed timeout can cause premature aborts.

Implement a **linear timeout backoff** so that each subsequent iteration gets more time. Default increment is **150000 ms** per iteration, with support for a maximum timeout cap to prevent runaway runtimes.

## Inputs / Related Topics

- Root Seed: [seed-increase-timeout-on-each-iteration-defau](topics/seed-increase-timeout-on-each-iteration-defau/seed.md)
- Session: seed-increase-timeout-on-each-iteration-defau@2026-02-10T13-02-10Z
- Related Spikes:
  - (none yet)

## Requirements

- Compute an **effective timeout** per iteration using a deterministic rule:
  - `effective = base + (iteration_index * increment)`
  - `effective = min(effective, max_timeout)` when `max_timeout` is configured
- Default `increment` is **150000 ms**.
- Define/confirm iteration semantics:
  - Clarify whether `iteration_index` starts at `0` (first attempt) or `1`.
- Configuration:
  - Expose `base_timeout_ms`, `increment_ms`, and optional `max_timeout_ms` in the appropriate configuration surface.
  - Ensure defaults are documented and versionable in repo config.
- Observability:
  - Log (or record) base, increment, iteration index, effective timeout, and whether max cap applied.
- Compatibility:
  - Preserve current behavior when backoff is disabled or when defaults match existing behavior.
- Test coverage:
  - Unit tests for timeout calculation (including cap behavior and iteration indexing).

## Constraints

- Default increment must be **150000 ms**.
- Must avoid runaway execution time (cap and/or max iteration limit must still be respected).
- Must be observable via logs.
- Keep behavior backwards compatible and predictable.

## Assumptions

- The retry/loop code has an accessible attempt counter at the point timeouts are computed.
- Timeouts are expressed as a single duration value (ms) that can be passed to the underlying enforcement mechanism.

## Risks & Gaps

- **Ambiguous target timeout** (which timeout are we changing?):
  - Mitigation: identify the concrete code path(s) where a timeout is enforced (per-ticket attempt, per-IRF phase, subprocess watchdog, etc.).
- **Off-by-one iteration indexing** leading to unexpected timeouts:
  - Mitigation: explicitly define and test the iteration index start value.
- **Masking real hangs** by allowing too much extra time:
  - Mitigation: encourage/require a `max_timeout_ms` cap and keep the increment linear.

## Work Plan (phases / tickets)

1. **Locate and document current timeout behavior**
   - Identify current timeout defaults and where they are configured.
   - Identify the iteration/attempt counter used in retries.
2. **Implement timeout backoff calculation**
   - Add helper function for effective timeout.
   - Wire it into the relevant retry/loop/attempt code path.
3. **Configuration + docs**
   - Add/extend settings and (if applicable) CLI flags.
   - Document semantics (units, indexing, cap behavior).
4. **Logging + tests**
   - Add structured logging of effective timeout.
   - Unit tests for calculation; light integration test if feasible.

## Acceptance Criteria

- [ ] Effective timeout increases linearly per iteration with default increment **150000 ms**.
- [ ] Optional `max_timeout_ms` cap is supported and enforced.
- [ ] Logs show iteration index and effective timeout (and cap usage).
- [ ] Unit tests cover base/increment/cap and indexing semantics.
- [ ] Configuration defaults are documented and do not unexpectedly change existing workflows.

## Open Questions

- Which timeout is being increased in this repo (per-ticket attempt, per-command, per-phase)?
- What is the current base timeout default and where is it defined?
- Should `iteration_index` start at 0 or 1?
- Should we add a global maximum cap by default (even if not explicitly configured)?

---

## Consultant Notes (Metis)

- 2026-02-10: Draft created from seed; needs follow-up spike/baseline scan to anchor to the exact timeout enforcement code path.

## Reviewer Notes (Momus)

- 2026-02-10: PASS|FAIL
  - Blockers:
    - (none yet)
  - Required changes:
    - (none yet)
