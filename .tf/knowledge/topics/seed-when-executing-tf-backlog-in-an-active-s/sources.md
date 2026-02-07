# Sources

## User Input

- when executing `/tf-backlog` in an active session started with `/tf-seed`, use this seed (and related spike and plan docs) automatically.

## Related Code Areas (to confirm during spike/plan)

- `tf_cli/session_store.py`
- backlog generation entry point (prompt/command) for `/tf-backlog`
- `tf_cli/ticket_factory.py` (ticket creation + dependency/link helpers)
