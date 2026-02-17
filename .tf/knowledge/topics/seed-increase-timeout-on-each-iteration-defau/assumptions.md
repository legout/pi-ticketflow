# Assumptions

- There is an iteration/attempt counter available at the point where timeouts are computed.
- Timeout enforcement can be expressed as a single numeric duration (e.g., ms) per attempt.
- Increasing the timeout on later iterations meaningfully improves completion rate (i.e., later attempts are not always doomed for other reasons).
