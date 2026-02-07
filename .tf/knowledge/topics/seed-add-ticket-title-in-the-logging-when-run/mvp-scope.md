# MVP Scope

## In Scope

- Add ticket title to verbose logging for `tf ralph`.
- Implement a single source of truth for “ticket display label” (ID + title) used by verbose logs.
- Cache title lookups per ticket during a run.

## Out of Scope (for MVP)

- Full structured logging overhaul.
- Changing `--quiet` / default output formats.
- UI/dashboard changes.
- Advanced redaction policies beyond a documented baseline.
