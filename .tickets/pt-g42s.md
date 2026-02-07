---
id: pt-g42s
status: closed
deps: [pt-az2p]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 2
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:cli]
---
# CLN-10: Remove or isolate legacy shell runtime path per deprecation policy

## Task
Execute deprecation policy by removing or isolating legacy shell runtime path.

## Context
Legacy shell fallback currently increases maintenance complexity.

## Acceptance Criteria
- [ ] scripts/tf_legacy.sh path removed or quarantined per policy
- [ ] CLI fallback wiring updated accordingly
- [ ] Rollback notes documented

## Constraints
- Follow approved deprecation timeline

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T16:21:17Z**

--note ## Implementation Complete

**Changes Made:**
1. Removed <code>scripts/tf_legacy.sh</code> (4,365 lines of legacy bash CLI)
2. Updated <code>tf_cli/cli.py</code>:
   - Removed <code>find_legacy_script()</code>, <code>run_legacy()</code> functions
   - Removed <code>legacy</code> command handler
   - Removed related helper functions (<code>raw_base_from_source()</code>, <code>ensure_tf_assets()</code>)
   - Updated help text (removed Legacy section)
3. Updated <code>docs/deprecation-policy.md</code>:
   - Marked <code>scripts/tf_legacy.sh</code> as **Removed**
   - Updated removal date to 2026-02-07
   - Completed Phase 3 milestones
   - Marked removal criteria checklist items complete

**Quality Checks:**
- Python syntax: PASS
- Shell syntax: PASS
- Manual review: PASS (0 critical/major/minor issues)

**Rollback:**
Restore from git: <code>git checkout <commit-before> -- scripts/tf_legacy.sh</code>
