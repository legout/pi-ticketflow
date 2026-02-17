# Assumptions

- The Ralph loop has (or can derive) a consistent notion of ticket state: ready, blocked, running, done.
- The Ralph loop already knows the dependency graph or can determine whether a ticket is runnable.
- Adding a small amount of additional logging/output formatting is acceptable and won’t break automation.
