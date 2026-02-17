# MVP Scope

## In Scope
- Add a Ralph execution backend that starts per-ticket background interactive shell sessions.
- Run `pi /tf <ticket-id> --auto` per ticket with fresh process/session isolation.
- Wire session lifecycle events into Ralph progress updates and ticket result handling.
- Support configurable parallel worker count using existing readiness/dependency/component filters.
- Provide commands/log hints for attaching to live sessions.

## Out of Scope (for MVP)
- Complex UI for session dashboards.
- Cross-machine/distributed worker orchestration.
- Advanced auto-healing beyond basic timeout/cleanup/retry policy.
- Replacing the existing backend immediately (ship as opt-in first).
