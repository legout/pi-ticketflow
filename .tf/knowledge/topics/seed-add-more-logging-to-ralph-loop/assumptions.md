# Assumptions

- The Ralph loop has a single main execution path where additional logging can be centralized.
- Users run Ralph from a terminal/CI where stdout/stderr is captured.
- Logging can be added without changing Ralph’s core workflow semantics.
- There is an acceptable way to enable debug verbosity (flag/env var) without breaking existing usage.
