# Success Metrics

- Running `tf ralph start --verbose` shows the ticket title for each ticket at least once at the beginning of processing.
- Verbose log lines that are clearly ticket-scoped include the ticket title (or a consistent fallback) alongside the ID.
- No regression in non-verbose output (same content/format as before).
- No significant performance regression (avoid repeated ticket lookups during a run).
