# Success Metrics

- Ralph can process tickets with `interactive_shell` background sessions end-to-end without manual intervention.
- Each completed ticket is traceable to a unique session ID and artifact path.
- Parallel mode increases throughput versus serial mode on component-safe backlogs.
- Users can attach to active sessions for live inspection without breaking loop orchestration.
- Failure handling is robust: stuck/failed sessions are detected, recorded, and retried/failed cleanly.
