---
id: plan-critical-cleanup-simplification
status: approved
last_updated: 2026-02-07
---

# Plan: Critical Cleanup and Simplification of pi-ticketflow

## Summary
This plan consolidates three cleanup reviews into one implementation program focused on reducing complexity, removing legacy drag, and making the project easier to maintain.

The highest risks are repository/state bloat, duplicated logic across CLI modules, and drift between code and docs. The cleanup should be executed in strict phases: first make the repo safe and lean, then converge architecture, then simplify naming and documentation, and finally harden quality gates.

## Requirements
- Reduce repository noise and accidental commits of runtime artifacts.
- Keep user-visible behavior stable during cleanup.
- Remove or isolate legacy code paths that are no longer required.
- Eliminate duplicated utility logic in CLI modules.
- Align docs/prompts with actual code and command behavior.
- Produce an ordered, dependency-aware cleanup backlog.

## Constraints
- Avoid risky “big bang” refactors.
- Each ticket should be executable in 1–2 hours.
- Preserve backward compatibility where still needed, but timebox deprecations.
- Keep cleanup changes testable and reversible (small PRs).

## Assumptions
- Python CLI is now the primary implementation.
- Existing test suite remains the safety net during refactor.
- Local runtime data in `.tf/` is not intended as long-term source-controlled product assets.

## Risks & Gaps
- Some users may still depend on `tf legacy` paths.
- Existing docs include mixed old/new command styles.
- Runtime data cleanup may require history rewrite decisions beyond normal commits.
- Coverage increase may expose hidden behavior coupling in low-tested modules.

## Work Plan (phases / tickets)
1. Repository hygiene + runtime artifact policy
2. Shared CLI utility extraction and dedup refactor
3. Legacy path deprecation/removal (timeboxed)
4. Naming convergence (`*_new.py` cleanup)
5. Documentation and prompt reconciliation
6. Quality gate hardening and missing tests

## Acceptance Criteria
- [x] Ordered cleanup backlog created with dependencies.
- [ ] Runtime artifacts and build noise are properly ignored and untracked.
- [ ] Duplicate helper logic is centralized and consumed by all relevant CLI modules.
- [ ] Legacy paths are either removed or clearly deprecated with policy/timeline.
- [ ] Docs and prompts accurately reflect current command/config behavior.
- [ ] Coverage gate is raised to a meaningful baseline with targeted test additions.

## Open Questions
- Should git history be rewritten to purge previously committed large runtime artifacts?
- What deprecation window is acceptable for removing `tf legacy` / `tf new` compatibility?
- Which historical root docs should be archived vs deleted?

---

## Consultant Notes (Metis)
- 2026-02-07: Consolidated findings from:
  - `CRITICAL_REVIEW_AND_CLEANUP_PLAN.md`
  - `CLEANUP_PLAN.md`
  - live codebase audit (repo size, tracked state, code duplication, docs drift, coverage profile)
- 2026-02-07: Key prioritization decision: do **repo hygiene first**, before architectural or naming refactors, to reduce blast radius and review noise.
- 2026-02-07: Backlog materialized in `tk` with dependency graph. Created IDs:
  `pt-e7hj, pt-mr22, pt-gzqg, pt-1vz2, pt-7sv0, pt-ynqf, pt-a51k, pt-0nqq, pt-az2p, pt-g42s, pt-np39, pt-pa5v, pt-1zkq, pt-mej4`.

## Reviewer Notes (Momus)
- 2026-02-07: PASS
  - Blockers:
    - none
  - Required changes:
    - backlog must explicitly include a compatibility/deprecation ticket before hard removal of legacy command paths
