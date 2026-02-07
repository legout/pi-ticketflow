# Success Metrics

- Running `/tf-backlog` with **no args** during an active session generates backlog tickets for the session’s root seed.
- Backlog generation includes relevant context from session-linked spikes/plan (when present).
- CLI output clearly reports which topic and session inputs were used.
- No behavior regression for users who always pass an explicit topic-id/path.
