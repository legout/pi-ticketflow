# Assumptions: seed-automatic-planning-sessions-linkage

- Knowledge base directory is writable and follows `workflow.knowledgeDir` (default `.tf/knowledge`).
- Topic structure is stable: `.tf/knowledge/topics/{topic-id}/...`.
- It is acceptable to add new files under `.tf/knowledge/` (e.g., `.active-planning.json`, `sessions/`).
- Existing tooling that reads `index.json` will tolerate additional keys (if we add them).
- Users generally plan one feature at a time; “active session” is a reasonable default.
