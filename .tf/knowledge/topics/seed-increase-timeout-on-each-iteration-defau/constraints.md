# Constraints

- Default timeout increment should be **150000 ms** per iteration.
- Must avoid runaway execution time (support a max timeout cap and/or respect a max iterations setting).
- Must be observable (log effective timeout per iteration).
- Keep behavior backwards compatible (avoid surprising timeouts for existing workflows).
