# Review: pt-oa8n

## Critical (must fix)
- `tf/ralph/queue_state.py:160` - Type annotation `Optional[callable]` uses lowercase `callable` which is the built-in function, not the type. Should be `Optional[Callable]` imported from `typing` or `collections.abc`. This will cause type checker errors.

## Major (should fix)
- `tf/ralph/queue_state.py:98` - The `blocked_tickets` set is built but never used. Either expose it as a property or remove the collection to avoid unnecessary memory allocation.

## Minor (nice to fix)
- `tf/ralph/queue_state.py:46-47` - The `__post_init__` validation allows negative counts. While `get_queue_state()` only produces non-negative counts, direct construction of `QueueStateSnapshot(-1, -1, -1, -1, -4)` passes validation. Consider adding non-negative checks.
- `tf/ralph/queue_state.py:8` - Missing `Callable` import from typing module (needed for the type annotation fix above).

## Warnings (follow-up ticket)
- `tf/ralph/queue_state.py:140` - No unit tests exist for this module (noted in implementation as pending pt-ri6k). The complexity of disjoint set validation and dep_graph logic warrants comprehensive test coverage.
- `tf/ralph/queue_state.py:180-185` - `get_queue_state_from_scheduler` eagerly builds the entire dep_graph even though only pending tickets need checking. If dep_resolver is expensive, this wastes work.

## Suggestions (follow-up ticket)
- `tf/ralph/queue_state.py:52` - Consider adding `from_queue_snapshot()` or similar to convert from existing Ralph scheduler state objects directly, reducing boilerplate for callers.
- `tf/ralph/queue_state.py:140-142` - Consider adding runtime type validation for the set/dict contents to fail fast if non-string values are passed.

## Summary Statistics
- Critical: 1
- Major: 1
- Minor: 2
- Warnings: 2
- Suggestions: 2

## Reviewer Sources
- reviewer-general: Critical(1), Major(1), Minor(1), Warnings(1), Suggestions(1)
- reviewer-spec-audit: Critical(0), Major(0), Minor(0), Warnings(0), Suggestions(0)
- reviewer-second-opinion: Critical(0), Major(1), Minor(2), Warnings(1), Suggestions(2)
