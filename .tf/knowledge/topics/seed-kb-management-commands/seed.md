# Seed: Knowledge base management commands (tf kb ...)

## Vision
Make `.tf/knowledge/` maintainable as it grows by providing first-class CLI tools (and optional Pi prompt wrappers later) to list, inspect, archive, delete, and validate knowledge topics.

## Core Concept
Implement a Python-native `tf kb` command group (NOT the legacy shell) that operates on the knowledge directory defined by `workflow.knowledgeDir` (default `.tf/knowledge`). It manages topic directories under `topics/` and keeps `index.json` consistent.

## Key Features (MVP)
- `tf kb ls` — list topics with filters (type/status) and sort by updated date.
- `tf kb show <topic-id>` — show metadata and paths to key docs.
- `tf kb archive <topic-id> [--reason ...]` — move topic under `{knowledgeDir}/archive/topics/` and update index.
- `tf kb restore <topic-id>` — move back to active topics and update index.
- `tf kb delete <topic-id>` — **permanent deletion** of the topic directory and removal from index.
- `tf kb validate` — detect index drift (missing paths, orphan topic dirs, duplicates).
- `tf kb rebuild-index [--dry-run]` — regenerate index from filesystem.

## Non-Goals (MVP)
- Full graph visualization.
- Auto-linking across seed/spike/plan (handled by the planning sessions feature).
- Remote/syncing knowledge.

## Open Questions
- Should `tf kb delete` require an explicit confirmation flag (e.g., `--yes`) even though it is permanent?
- Should archived topics remain in index with an `archived: true` field, or be removed from index and discoverable via `--archived` scanning?
