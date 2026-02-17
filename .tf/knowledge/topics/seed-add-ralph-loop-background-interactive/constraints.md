# Constraints

- Must preserve current Ralph safety semantics (dependency ordering, component isolation in parallel mode).
- Must not require user interaction to complete tickets in autonomous runs.
- Must guarantee cleanup/termination of background sessions to avoid resource leaks.
- Must keep implementation incremental (MVP in small tickets, 1–2 hours each).
- Must maintain compatibility with existing `tf ralph status`, progress files, and lessons flow.
