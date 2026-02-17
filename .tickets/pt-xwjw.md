---
id: pt-xwjw
status: closed
deps: []
links: [pt-bcu8]
created: 2026-02-10T13:11:20Z
type: task
priority: 2
assignee: legout
external-ref: seed-increase-timeout-on-each-iteration-defau
tags: [tf, backlog, component:config, component:docs, component:workflow]
---
# Define timeout backoff semantics + configuration keys

## Task
Define exactly how per-iteration timeout backoff is computed and where it is configured.

## Context
We want to increase timeout on each iteration/attempt so later retries get more time.

Plan notes: Implement linear timeout backoff: effective = base + iteration_index * increment (cap with max_timeout when configured). Default increment = 150000 ms.

## Acceptance Criteria
- [ ] Iteration index semantics are explicit (starts at 0 vs 1)
- [ ] Effective timeout formula is documented (including optional max cap)
- [ ] Config keys and defaults are defined (base, increment=150000, max cap)

## Constraints
- Default increment: **150000 ms** per iteration
- Avoid runaway execution time (support max cap and respect max iterations)
- Backwards compatible defaults / behavior

## References
- Seed: seed-increase-timeout-on-each-iteration-defau
- Plan: plan-increase-timeout-on-each-iteration-defau


## Notes

**2026-02-10T13:58:56Z**

--note Defined timeout backoff semantics and configuration keys.

Specification includes:
- Zero-based iteration index semantics (starts at 0)
- Effective timeout formula: base + (iteration * increment), with optional max cap
- Configuration keys: timeoutBackoff.enabled, baseTimeoutMs, incrementMs (150000), maxTimeoutMs
- Validation constraints and error logging requirements
- Input validation for calculate_effective_timeout() function
- Edge case test requirements
- Integer overflow safeguards

All review feedback addressed (2 Critical, 4 Major issues fixed).

Commit: 85b68fa
Blocking pt-bcu8 for implementation.

**2026-02-10T14:00:58Z**

## Implementation Complete

Timeout backoff semantics and configuration keys have been defined and documented.

### Deliverables
- **timeout-backoff-spec.md**: Complete specification document covering:
  - Zero-based iteration index semantics with RetryState mapping
  - Effective timeout formula:  with optional max cap
  - Configuration schema with defaults (base=600000, increment=150000, max=null)
  - Comprehensive validation rules and error handling
  - Environment variable overrides (RALPH_TIMEOUT_BACKOFF_*)
  - Observability requirements (log format, structured fields)
  - Test requirements including edge cases

### Acceptance Criteria
- ✅ Iteration index semantics explicit (0-indexed, maps from 1-indexed RetryState)
- ✅ Effective timeout formula documented with max cap support
- ✅ Config keys defined with defaults matching existing Ralph settings

### Implementation Notes
- Specification reviewed against actual codebase (ralph.py, retry_state.py)
- All Critical and Major review issues addressed
- Quality gate passed (0 Critical, 0 Major remaining)
- Blocking dependency for pt-bcu8 (implementation ticket) ready

### Commit
a478272 pt-xwjw: Define timeout backoff semantics and configuration keys
