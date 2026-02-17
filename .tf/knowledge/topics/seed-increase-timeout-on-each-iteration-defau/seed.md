# Seed: Increase timeout on each iteration (default +150000 ms)

## Vision

Avoid premature failures for work that tends to take longer on later retries/iterations by gradually increasing the allowed timeout per attempt.

## Core Concept

Implement a per-iteration timeout backoff:

- Start with a base timeout.
- For each subsequent iteration, increase timeout by a fixed increment.
- Default increment: **150000 ms** per iteration.
- Optionally enforce a max timeout cap.

## Key Features

1. Configurable base timeout, increment, and optional maximum cap
2. Deterministic calculation of effective timeout per iteration (no hidden state)
3. Clear logging: base, increment, iteration index, effective timeout, and whether a cap was applied
4. Backwards-compatible defaults (existing behavior unchanged unless configured / defaulted intentionally)

## Open Questions

- Which timeout is being increased (per-ticket run, per-command invocation, or per-quality-gate step)?
- What are the current timeout defaults and where are they configured?
- Should the increment apply starting at iteration 2 (i=1) or iteration 1 (i=0)?
- Do we need exponential backoff support later, or is linear (+150000) sufficient?
- What is a safe maximum timeout cap to prevent excessively long runs?
