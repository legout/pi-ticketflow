# Constraints

- Must remain backward compatible with explicit-argument usage.
- Avoid introducing surprising implicit behavior; if session is used, log that fact.
- Keep tickets small/self-contained; do not require users to open multiple docs to implement a ticket.
- Do not break session finalization semantics (archiving/deactivation) on successful backlog creation.
