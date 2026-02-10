# Review: pt-oa8n

## Overall Assessment
The implementation provides a clean, well-documented queue-state snapshot helper for Ralph's scheduler. The code follows Python best practices with frozen dataclasses, proper docstrings, and clear separation of concerns. The semantics correctly implement the specification from pt-m54d with appropriate validation and error handling.

## Critical (must fix)
- `tf/ralph/queue_state.py:160` - Type annotation `Optional[callable]` uses lowercase `callable` which is the built-in function, not the type. Should be `Optional[Callable]` imported from `typing` or `collections.abc`. This will cause type checker errors.

## Major (should fix)
- `tf/ralph/queue_state.py:98` - The `blocked_tickets` set is built but never used. Either expose it as a property or remove the collection to avoid unnecessary memory allocation.

## Minor (nice to fix)
- `tf/ralph/queue_state.py:46-47` - The `__post_init__` validation allows negative counts (e.g., `ready=-1`). While `get_queue_state()` only produces non-negative counts, direct construction of `QueueStateSnapshot(-1, -1, -1, -1, -4)` passes validation. Consider adding non-negative checks.

## Warnings (follow-up ticket)
- `tf/ralph/queue_state.py:140` - No unit tests exist for this module (noted in implementation as pending pt-ri6k). The complexity of disjoint set validation and dep_graph logic warrants comprehensive test coverage.

## Suggestions (follow-up ticket)
- `tf/ralph/queue_state.py:52` - Consider adding `from_queue_snapshot()` or similar to convert from existing Ralph scheduler state objects directly, reducing boilerplate for callers.

## Positive Notes
- Excellent docstring coverage with type hints, examples, and complexity analysis
- `frozen=True` dataclass correctly implements immutable snapshot semantics
- Proper disjoint set validation with clear error messages
- Blocked ticket detection correctly checks `dep_graph[ticket]` is non-empty (not just presence in map)
- Format methods (`__str__` and `to_log_format`) match the specification exactly
- The convenience wrapper `get_queue_state_from_scheduler()` provides flexible API options
- Good separation between the immutable snapshot data and the computation function

## Summary Statistics
- Critical: 1
- Major: 1
- Minor: 1
- Warnings: 1
- Suggestions: 1
