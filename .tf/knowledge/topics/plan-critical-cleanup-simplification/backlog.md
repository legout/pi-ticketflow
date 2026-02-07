# Backlog: plan-critical-cleanup-simplification

## Ordered Tickets

| Alias | tk ID | Title | Priority | Est. Hours | Depends On |
|------|-------|-------|----------|------------|------------|
| CLN-01 | pt-e7hj | Define runtime artifact policy for `.tf/`, `.tickets/`, and generated outputs | P0 | 1-2 | - |
| CLN-02 | pt-mr22 | Expand `.gitignore` for Python/build/runtime artifacts and project-specific state | P0 | 1-2 | CLN-01 |
| CLN-03 | pt-gzqg | Untrack already-committed runtime/build artifacts without deleting local data | P0 | 1-2 | CLN-02 |
| CLN-04 | pt-1vz2 | Add repo-size guardrail checks (large file + forbidden-path CI/pre-commit checks) | P1 | 1-2 | CLN-03 |
| CLN-05 | pt-7sv0 | Extract shared CLI utilities (`find_project_root`, `read_json`, merge helpers, etc.) to common module | P1 | 1-2 | CLN-03 |
| CLN-06 | pt-ynqf | Refactor CLI modules to consume shared utilities (no behavior change pass) | P1 | 1-2 | CLN-05 |
| CLN-07 | pt-a51k | Extract shared frontmatter/model-sync logic and remove duplicate implementations | P1 | 1-2 | CLN-06 |
| CLN-08 | pt-0nqq | Reconcile asset update/install paths (`update_new` vs `project_bundle`) into one source of truth | P1 | 1-2 | CLN-06 |
| CLN-09 | pt-az2p | Introduce explicit deprecation policy for `tf legacy` and `tf new` namespaces | P1 | 1-2 | CLN-06 |
| CLN-10 | pt-g42s | Remove or isolate legacy runtime path (`scripts/tf_legacy.sh` + fallback wiring) per policy | P2 | 1-2 | CLN-09 |
| CLN-11 | pt-np39 | Rename `*_new.py` modules to stable names and update imports/tests/docs | P2 | 1-2 | CLN-10 |
| CLN-12 | pt-pa5v | Fix docs/prompt drift (command examples, config key names, Ralph logging behavior, stale template commands) | P1 | 1-2 | CLN-07 |
| CLN-13 | pt-1zkq | Archive or relocate stale root-level historical docs (`proposal*`, reports, stray files) with traceability | P3 | 1-2 | CLN-12 |
| CLN-14 | pt-mej4 | Raise coverage gate incrementally and add tests for currently low-coverage user-facing modules | P1 | 1-2 | CLN-11, CLN-12 |

---

## Ticket Details

### CLN-01 — Define runtime artifact policy
**Task**: Document exactly what is source-of-truth code vs runtime/generated state.
**Acceptance Criteria**:
- Policy file exists and is linked from README/contributing docs.
- Includes explicit handling for `.tf/knowledge`, `.tf/ralph/sessions`, `.tickets`, `htmlcov`, `*.egg-info`.

### CLN-02 — Expand `.gitignore`
**Task**: Add comprehensive ignores for Python/build/runtime noise.
**Acceptance Criteria**:
- `.gitignore` covers `__pycache__`, `*.pyc`, `.pytest_cache`, `htmlcov`, `*.egg-info`, runtime session artifacts.
- `git status` no longer shows expected generated files after test/run cycles.

### CLN-03 — Untrack existing runtime/build artifacts
**Task**: Remove tracked generated/runtime content from git index while preserving local files.
**Acceptance Criteria**:
- Large runtime/session artifacts no longer in git index.
- Working tree still usable locally.
- Migration note included for contributors.

### CLN-04 — Add size/forbidden-path guardrails
**Task**: Add automation to block accidental commits of large/runtime artifacts.
**Acceptance Criteria**:
- CI/pre-commit check fails on forbidden paths and oversized files.
- Documented override/escalation path for intentional large assets.

### CLN-05 — Extract shared CLI utilities
**Task**: Create shared utility module for duplicated helper functions.
**Acceptance Criteria**:
- Common module introduced with tests.
- At least root-resolution and JSON helpers moved.

### CLN-06 — Refactor modules to shared utilities
**Task**: Replace duplicate helper definitions in CLI modules with imports.
**Acceptance Criteria**:
- Duplicate helper implementations removed from target modules.
- Behavior unchanged; tests pass.

### CLN-07 — Consolidate frontmatter/model-sync logic
**Task**: Unify duplicated sync logic currently split across modules/scripts.
**Acceptance Criteria**:
- Single implementation path for model/frontmatter updates.
- `tf sync` behavior validated in tests.

### CLN-08 — Converge install/update asset flows
**Task**: Remove duplicated manifest/update logic and standardize on one asset flow.
**Acceptance Criteria**:
- One source-of-truth install/update planner remains.
- `init/sync/update` commands still operate correctly.

### CLN-09 — Define deprecation policy for legacy namespaces
**Task**: Add explicit timeline and compatibility policy for `tf legacy` and `tf new`.
**Acceptance Criteria**:
- Policy documented with milestones.
- CLI emits clear deprecation messages where relevant.

### CLN-10 — Remove/isolate legacy shell path
**Task**: Execute policy by removing or quarantining `tf_legacy.sh` and fallback hooks.
**Acceptance Criteria**:
- Legacy path no longer part of default runtime.
- Rollback strategy documented.

### CLN-11 — Rename `*_new.py` modules
**Task**: Rename transitional modules and update imports/references.
**Acceptance Criteria**:
- No runtime references to old names.
- Tests and CLI entrypoints pass.

### CLN-12 — Reconcile docs and prompts
**Task**: Update stale docs and prompt command/config references.
**Acceptance Criteria**:
- `README`, `docs/*`, and prompt help agree on command syntax and config structure.
- Known stale references (e.g., old commands, old model keys, logging behavior mismatches) resolved.

### CLN-13 — Archive stale root docs
**Task**: Move historical analysis docs to archive location or remove if obsolete.
**Acceptance Criteria**:
- Root directory contains only active project assets.
- Archived docs remain discoverable if retained.

### CLN-14 — Raise quality gates + fill test gaps
**Task**: Increase coverage floor in steps and add tests for low-coverage user-facing modules.
**Acceptance Criteria**:
- Coverage threshold raised from current low baseline to an agreed target path.
- New tests added for setup/login/tags/seed/agentsmd and other low-covered modules.
