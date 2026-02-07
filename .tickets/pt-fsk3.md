---
id: pt-fsk3
status: closed
deps: [pt-6rja]
links: []
created: 2026-02-06T13:07:53Z
type: task
priority: 2
assignee: legout
external-ref: plan-kb-management-cli
tags: [tf, backlog, plan, knowledge]
---
# Implement kb helpers: knowledgeDir resolve + atomic index.json IO

## Task
Implement shared helper functions for kb commands:
- resolve knowledgeDir from `config/settings.json` (`workflow.knowledgeDir`, default `.tf/knowledge`)
- support `--knowledge-dir` override
- atomic read/write for `.tf/knowledge/index.json`

## Acceptance Criteria
- [ ] Helper returns correct knowledgeDir in project root.
- [ ] Atomic writes use tmp + rename.
- [ ] Functions are covered by unit tests.

## Constraints
- stdlib only.

## References
- Plan: plan-kb-management-cli



## Notes

**2026-02-06T13:20:05Z**

Implementation complete. Created kb_helpers.py with:

- resolve_knowledge_dir(): Resolves knowledgeDir from config with CLI override support
  Priority: --knowledge-dir > TF_KNOWLEDGE_DIR env > config > default
  
- atomic_read_index(): Atomically reads index.json with error handling

- atomic_write_index(): Atomic writes using tmp+rename pattern

- ensure_index_exists(): Creates index.json if missing

Refactored kb_cli.py to use new helpers. Added 23 unit tests, all passing.

Commit: c052a71
