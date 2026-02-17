# Success Metrics

- Timeout-related failures decrease for workloads that legitimately need more time on later iterations.
- Logs make it obvious what timeout was applied for a given iteration and why.
- The timeout backoff does not cause unbounded runtimes (cap and/or max iterations are respected).
- Default behavior is predictable and documented (including the +150000 ms increment default).
