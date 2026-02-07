# Assumptions

- The `tk` CLI supports reading ticket metadata and updating a ticket’s priority.
- Tickets contain enough signals (tags/title/description) to make a reasonable rubric-based classification.
- A small amount of manual override is acceptable when the rubric cannot decide.
- The new Pi command can be implemented as a prompt entry point without requiring major refactors.
