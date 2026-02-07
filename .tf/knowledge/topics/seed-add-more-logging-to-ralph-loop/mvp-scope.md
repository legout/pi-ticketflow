# MVP Scope

## In Scope
- Add consistent log lines for:
  - run start/end
  - each iteration start/end
  - ticket selection (picked/skipped + reason)
  - phase transitions
  - unhandled exceptions / failures (single summary line)
- Add a simple verbosity mechanism (`--verbose` or `RALPH_LOG_LEVEL=debug`).

## Out of Scope (for MVP)
- Full structured JSON logging with schema guarantees.
- Metrics/telemetry pipeline integration.
- Persisted log rotation / retention policies.
- Deep per-tool tracing for every subagent/tool call.
