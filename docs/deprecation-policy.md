# Deprecation Policy for TF Legacy Namespaces

**Document Version:** 1.0  
**Effective Date:** 2026-02-07  
**Last Updated:** 2026-02-07  
**Status:** Active  
**Ticket:** pt-az2p

---

## 1. Executive Summary

This document defines the deprecation policy for legacy TF (TicketFlow) namespaces and artifacts that have been superseded by modern Python CLI implementations. This policy establishes clear timelines, migration paths, and communication strategies to ensure a smooth transition for all users.

### Deprecation Scope

| Namespace/Artifact | Status | Replacement | Deprecation Notice | Removal Target |
|-------------------|--------|-------------|-------------------|----------------|
| `scripts/tf_legacy.sh` | Deprecated | `tf_cli/` Python modules | 2026-02-07 | 2026-04-01 |
| `*_new.py` module suffix | Deprecated | Remove `_new` suffix | 2026-02-07 | 2026-03-15 |
| `tf new` command prefix | Deprecated | Direct `tf` commands | 2026-02-07 | 2026-03-01 |

---

## 2. Deprecation Timeline

### Phase 1: Notice Period (Now - 2026-02-28)

**Duration:** 3 weeks  
**Status:** Active

During this phase:
- All legacy artifacts remain functional
- Deprecation warnings added to affected code paths
- Documentation updated to reflect new preferred approaches
- Migration guide published

**Milestones:**
- [x] Deprecation policy published (2026-02-07)
- [ ] Add deprecation warnings to `tf_legacy.sh` entry points
- [ ] Update CLI help text to prefer non-`_new` command names
- [ ] Publish migration guide

### Phase 2: Soft Deprecation (2026-03-01 - 2026-03-31)

**Duration:** 4 weeks  
**Status:** Planned

During this phase:
- Legacy artifacts remain available but emit warnings
- CI/CD pipelines should migrate to new commands
- Documentation prioritizes new approaches

**Milestones:**
- [ ] `tf_legacy.sh` emits warning on invocation
- [ ] `_new.py` imports emit `DeprecationWarning`
- [ ] `tf new` commands show migration hint

### Phase 3: Hard Deprecation (2026-04-01 onwards)

**Duration:** Permanent  
**Status:** Planned

During this phase:
- Legacy artifacts are removed
- Only modern Python CLI remains
- Documentation references removed

**Milestones:**
- [ ] Delete `scripts/tf_legacy.sh`
- [ ] Rename all `*_new.py` → `*.py`
- [ ] Remove `tf new` command aliases
- [ ] Archive deprecation policy to `docs/history/`

---

## 3. Detailed Artifact Policies

### 3.1 Legacy Bash Script (`scripts/tf_legacy.sh`)

**Current State:**
- 4,078 lines of bash code
- Implements: `ralph`, `agentsmd`, `seed`, `track`, `next`, `backlog-ls`, `login`, `sync`, `update`, `doctor`
- **Not currently invoked** by any active code path (`find_legacy_script()` returns None)
- Full feature parity achieved in Python CLI

**Migration Path:**
```bash
# Old (deprecated)
./scripts/tf_legacy.sh doctor

# New (preferred)
tf doctor
# or
python -m tf_cli.cli doctor
```

**Removal Criteria:**
1. [ ] All CI/CD pipelines verified using Python CLI
2. [ ] Zero open tickets referencing `tf_legacy.sh` direct invocation
3. [ ] 30-day warning period elapsed since notice
4. [ ] Rollback plan tested (restore from git history)

### 3.2 _new.py Module Suffix

**Current State:**
- 13 modules with `_new` suffix indicating incomplete migration
- Creates confusion about which files are "active"
- Suggests temporary/transition state that has persisted

**Affected Files:**
| Current Name | Target Name | Notes |
|--------------|-------------|-------|
| `ralph_new.py` | `ralph.py` | Main Ralph loop implementation |
| `doctor_new.py` | `doctor.py` | Diagnostics command |
| `sync_new.py` | `sync.py` | Config sync command |
| `init_new.py` | `init.py` | Project initialization |
| `setup_new.py` | `setup_cmd.py` | Setup command (avoid setuptools conflict) |
| `login_new.py` | `login.py` | Authentication command |
| `next_new.py` | `next.py` | Queue navigation |
| `track_new.py` | `track.py` | Change tracking |
| `backlog_ls_new.py` | `backlog_ls.py` | Backlog listing |
| `agentsmd_new.py` | `agentsmd.py` | AGENTS.md management |
| `priority_reclassify_new.py` | `priority_reclassify.py` | Priority management |
| `tags_suggest_new.py` | `tags_suggest.py` | Component tagging |
| `update_new.py` | `update.py` | Update command |

**Migration Path:**
```python
# Old import (deprecated)
from tf_cli.doctor_new import run_doctor

# New import (preferred)
from tf_cli.doctor import run_doctor
```

**Removal Criteria:**
1. [ ] All imports updated in `cli.py`
2. [ ] All test imports updated
3. [ ] Backward compatibility shim added (optional, 2-week period)
4. [ ] Documentation references updated

### 3.3 `tf new` Command Prefix

**Current State:**
- Some commands accessible via `tf new <subcommand>`
- Indicates migration from legacy to new command structure
- Creates unnecessary typing overhead

**Affected Commands:**
```bash
# Deprecated forms
tf new priority-reclassify
tf new backlog-ls

# Preferred forms
tf priority-reclassify
tf backlog-ls
```

**Migration Path:**
- Commands work without `new` prefix
- Update scripts and documentation

**Removal Criteria:**
1. [ ] All internal references updated
2. [ ] Documentation migrated
3. [ ] Shell aliases/shortcuts updated in configs

---

## 4. Communication Strategy

### 4.1 User Communication

**Immediate Actions (Week 1):**
- Post deprecation notice to project README
- Add warning banner to `tf_legacy.sh` on execution
- Update `--help` output to show preferred commands

**Short-term Actions (Weeks 2-4):**
- Email/announce to active users
- Update project documentation site
- Add migration examples to common issues

**Pre-reminder Actions (1 week before removal):**
- Final warning in CLI output
- Socialize timeline in community channels

### 4.2 Internal Communication

**Development Team:**
- Update CONTRIBUTING.md with new naming conventions
- Add pre-commit hooks to prevent `_new.py` naming
- Code review checklist includes deprecation checks

**CI/CD Maintenance:**
- Audit all pipelines for legacy script usage
- Update deployment scripts
- Test rollback procedures

### 4.3 Migration Support

**Resources Provided:**
1. Migration guide (see Section 5)
2. Example before/after code snippets
3. Compatibility shim for `_new.py` imports (2-week window)
4. Git history reference for removed scripts

---

## 5. Migration Guide

### 5.1 Quick Reference

| If you were using... | Now use... |
|---------------------|------------|
| `scripts/tf_legacy.sh doctor` | `tf doctor` |
| `scripts/tf_legacy.sh sync` | `tf sync` |
| `from tf_cli.doctor_new import *` | `from tf_cli.doctor import *` |
| `tf new priority-reclassify` | `tf priority-reclassify` |
| `tf new backlog-ls` | `tf backlog-ls` |

### 5.2 Automated Migration

For common patterns, use these sed commands:

```bash
# Update Python imports
sed -i 's/from tf_cli\.\([a-z0-9_]*\)_new import/from tf_cli.\1 import/g' tf_cli/*.py

# Update shell script invocations
sed -i 's/scripts\/tf_legacy.sh/tf/g' *.sh
```

### 5.3 Verification Checklist

After migration, verify:
- [ ] `tf doctor` runs without errors
- [ ] `tf sync` updates configurations correctly
- [ ] All custom scripts use new import paths
- [ ] CI/CD pipelines pass
- [ ] No references to `_new.py` in codebase

---

## 6. Removal Criteria Checklist

Before final removal of each artifact, the following must be satisfied:

### General Criteria (All Artifacts)
- [ ] Deprecation notice period elapsed (minimum 30 days)
- [ ] Zero known blocking issues in migration tracker
- [ ] Rollback plan documented and tested
- [ ] Team sign-off on removal date

### `scripts/tf_legacy.sh` Specific
- [ ] All CI/CD pipelines migrated
- [ ] No direct script invocations in documentation
- [ ] Git backup verified (git history retains file)
- [ ] Removal ticket created (CLN-10: pt-g42s)

### `_new.py` Suffix Specific
- [ ] All imports updated in source files
- [ ] All imports updated in tests
- [ ] Import compatibility shim tested (if provided)
- [ ] `cli.py` command routing updated

### `tf new` Prefix Specific
- [ ] All documentation updated
- [ ] All internal scripts updated
- [ ] Command alias removed from CLI parser

---

## 7. Rollback Plan

If issues arise post-removal:

### Immediate Rollback (< 24 hours)
1. Restore from git: `git checkout <commit> -- scripts/tf_legacy.sh`
2. Re-add import compatibility shims
3. Notify team of temporary restoration

### Extended Rollback (> 24 hours)
1. Create hotfix branch
2. Re-implement removed functionality in Python
3. Mark as temporary compatibility layer
4. Set new removal date

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Migration completion | 100% | Zero references to legacy artifacts |
| User issues | < 5 | Support tickets post-removal |
| CI/CD failures | 0 | Pipeline success rate |
| Code clarity | Improved | Reduced confusion about active code |

---

## 9. Related Tickets

| Ticket | Description | Status |
|--------|-------------|--------|
| pt-az2p | Define deprecation policy (this work) | In Progress |
| pt-g42s | Remove legacy shell runtime per policy | Blocked |
| pt-ynqf | Dependency - prerequisite cleanup | Open |

---

## 10. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-07 | TF Team | Initial deprecation policy |

---

## Appendix A: Quick Command Reference

### Check for Legacy Usage
```bash
# Find direct script invocations
grep -r "tf_legacy.sh" --include="*.sh" --include="*.py" --include="*.yml" .

# Find _new.py imports
grep -r "_new import" --include="*.py" .
grep -r "from tf_cli.*_new" --include="*.py" .

# Find tf new commands
grep -r "tf new " --include="*.sh" --include="*.md" .
```

### Test Migration
```bash
# Verify Python CLI works
tf doctor
tf sync
tf --help

# Verify imports work
python -c "from tf_cli.doctor import run_doctor; print('OK')"
python -c "from tf_cli.sync import sync_config; print('OK')"
```
