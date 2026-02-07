---
id: pt-1vz2
status: closed
deps: [pt-gzqg]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:tests, component:workflow]
---
# CLN-04: Add CI/pre-commit guardrails for oversized and forbidden artifact paths

## Task
Add repository guardrails to prevent recommitting large files and forbidden runtime paths.

## Context
After cleanup, automation should prevent regressions in repository hygiene.

## Acceptance Criteria
- [ ] Check fails for oversized files above agreed threshold
- [ ] Check fails for forbidden runtime/build paths
- [ ] Guardrail behavior documented

## Constraints
- Keep checks fast for local contributors

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T15:26:46Z**

## Implementation Complete

**Commit:** 087b5be

**Summary:**
Added repository guardrails to prevent committing oversized files (>5MB) and forbidden runtime/build paths.

**Files Added:**
- ============================================================
REPOSITORY GUARDRAILS CHECK
============================================================

✅ All checks passed (197 files checked)
   - Max file size: 5MB
   - Forbidden patterns: 26 - Main checking script (26 forbidden patterns, configurable thresholds)
- ⚠️  A pre-commit hook already exists. - Pre-commit hook installer with backup support
-  - CI workflow with guardrails as first check
-  - Comprehensive documentation

**Pre-commit Hook:**
Installed at No files to check. - runs automatically on each commit.

**Review Issues Fixed:**
- 3 Critical: Fixed regex anchoring (venv, env, .env patterns), fixed docs error
- 4 Major: Moved subprocess imports to module level, improved .gitignore handling

**Verification:**
- All 193 repository files pass guardrails check
- Pre-commit hook installed and functional
- CI workflow ready for GitHub Actions

Run ============================================================
REPOSITORY GUARDRAILS CHECK
============================================================

✅ All checks passed (197 files checked)
   - Max file size: 5MB
   - Forbidden patterns: 26 for manual checks.

