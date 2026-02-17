# MVP Scope

## In Scope

- Compute effective timeout as: `effective = min(max_timeout, base_timeout + iteration * increment)`.
- Default `increment = 150000` (ms).
- Add/extend configuration surface (settings and/or CLI flag) for base, increment, and cap.
- Add logging that prints iteration index and effective timeout.
- Add tests for timeout calculation (including cap behavior).

## Out of Scope (for MVP)

- Exponential backoff strategies.
- Adaptive timeouts based on historical runtime.
- UI/visualizations beyond basic logs.
