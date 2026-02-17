# Constraints

- Must avoid infinite loops in Ralph: retries need a cap and/or a “blocked” outcome.
- Changes should be small and backwards compatible with existing `/tf` behavior.
- The retry/escalation policy must be configurable (different teams have different cost tolerances).
- Must not leak secrets into logs/artifacts when recording retry/escalation context.
