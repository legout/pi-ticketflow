# Success Metrics

- Progress output clearly shows **ready** and **blocked** ticket counts throughout the run.
- Normal logging prints ready/blocked counts at ticket **start** and **finish**.
- Counts remain correct as tickets unblock (dependency satisfaction) without confusing jumps.
- No noticeable slowdown from computing counts (especially in large ticket sets).
