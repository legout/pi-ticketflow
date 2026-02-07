---
id: plan-kb-management-cli
status: approved
last_updated: 2026-02-06
---

# Plan: Knowledge base management commands (tf kb ...)

## Summary
Add Python-native `tf kb ...` commands to manage the TF knowledge base (`.tf/knowledge/`). This provides deterministic tooling to list/show topics, archive/restore topics, permanently delete topics, and validate/rebuild the topic index.

Implementation must live in `tf_cli/` and be dispatched by the Python CLI (not `scripts/tf_legacy.sh`).

## Requirements
### Command surface (MVP)
- `tf kb ls`:
  - Lists topics from `{knowledgeDir}/index.json`.
  - Filters: `--type seed|plan|spike|baseline` (inferred from topic id prefix or files present).
  - Filters: `--status <value>` when topic has frontmatter `status:` (plans) (optional best-effort).
  - Flags: `--archived` to include archived topics in listing (scan `{knowledgeDir}/archive/topics/`).
- `tf kb show <topic-id>`:
  - Prints topic title/id and paths to key docs (overview/sources + main doc if present).
  - Prints whether topic is archived.
- `tf kb archive <topic-id> [--reason TEXT]`:
  - Moves `{knowledgeDir}/topics/<id>/` → `{knowledgeDir}/archive/topics/<id>/`.
  - Removes entry from active `index.json`.
  - Writes/updates a small `archive.md` in the archived topic dir with timestamp + reason (optional).
- `tf kb restore <topic-id>`:
  - Moves archived topic back to active topics dir.
  - Adds entry back to `index.json`.
- `tf kb delete <topic-id>`:
  - **Permanent deletion** of the topic directory (active or archived).
  - Removes entry from `index.json` if present.
  - Must be explicit about what was deleted (print path).
- `tf kb validate`:
  - Detect missing paths for entries in `index.json`.
  - Detect orphan topic dirs (present on disk but missing from index).
  - Detect duplicate IDs.
  - Non-zero exit on errors.
- `tf kb rebuild-index [--dry-run]`:
  - Scans `{knowledgeDir}/topics/*` and regenerates an `index.json` in canonical format.
  - `--dry-run` prints what would change.

### KnowledgeDir resolution
- Respect `workflow.knowledgeDir` from `config/settings.json` (default `.tf/knowledge`).
- Allow overriding via `--knowledge-dir <path>` on all kb commands.

### Determinism + safety
- All operations must be deterministic; no model calls.
- `index.json` writes should be atomic (tmp + rename).
- Delete is permanent (per request). (We may still require `--yes` confirmation; see Open Questions.)

## Constraints
- Implement in Python (`tf_cli/`), and make it reachable via `python -m tf_cli.cli kb ...`.
- Do not use `scripts/tf_legacy.sh`.
- Prefer stdlib only.

## Assumptions
- Active topics live under `{knowledgeDir}/topics/`.
- `index.json` is the source of truth for *active* topics.

## Risks & Gaps
- Permanent deletion is irreversible.
  - Mitigation: require a confirmation flag (`--yes`) or interactive prompt (decision needed).
- Index rebuild might reorder entries and cause noisy diffs.
  - Mitigation: stable sorting by topic id.

## Work Plan (phases / tickets)
1. Add Python CLI dispatch for `kb` in `tf_cli/cli.py` (bypass legacy).
2. Implement `tf_cli/kb_new.py` (argparse) with subcommands.
3. Implement shared helpers:
   - resolve knowledgeDir
   - read/write index.json atomically
   - scan topic dirs and infer metadata
4. Implement subcommands in order: `ls`, `show`, `archive`, `restore`, `delete`, `validate`, `rebuild-index`.
5. Add tests (tmp dirs) for archive/restore/delete and index rebuild/validate.
6. Document usage in README or docs.

## Acceptance Criteria
- [ ] `tf kb ls` and `tf kb show` work in a repo with `.tf/knowledge`.
- [ ] `tf kb archive` moves topic and updates index.
- [ ] `tf kb restore` reverses archive.
- [ ] `tf kb delete` permanently deletes and updates index.
- [ ] `tf kb validate` detects broken index entries and orphans.
- [ ] `tf kb rebuild-index --dry-run` shows changes without writing.
- [ ] All commands support `--knowledge-dir` override.

## Open Questions
- Should `tf kb delete` require `--yes` (still permanent, but reduces accidents), or delete immediately?

---

## Consultant Notes (Metis)
- 2026-02-06: Draft created. Keep index handling atomic and stable; implement delete with a safety confirmation even if the operation is permanent.

## Reviewer Notes (Momus)
- 2026-02-06: PASS
  - Notes:
    - Scope is crisp and deterministic.
    - Permanent delete is risky; suggest `--yes` confirmation.
