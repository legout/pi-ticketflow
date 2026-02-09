# Review: pt-7mvl

## Critical (must fix)
- **Decision clarity for pt-ihfv**: The implementation.md recommends "proceed with caution" and suggests an alternative approach (making `--session` optional), which creates ambiguity for the dependent ticket pt-ihfv ("Remove pi --session forwarding"). The seed explicitly asks for removal, but the analysis doesn't definitively decide between removal vs. the optional-config approach. A clear decision must be documented to unblock pt-ihfv.

## Major (should fix)
- **Missing clear "Decision" section**: The implementation document lacks a definitive "Decision" section that explicitly states: (1) whether to proceed with removal or the optional-config approach, (2) what the source of truth for session selection will be, and (3) explicit guidance for pt-ihfv implementers.
- **Alternative approach not evaluated against seed criteria**: The suggestion to make `--session` optional via `forwardSession: false` config is presented but not evaluated against the seed's acceptance criteria, which explicitly asks for removal.

## Minor (nice to fix)
- **Title/recommendation mismatch**: The ticket title says "without forwarding" but the document later recommends making it optional rather than removing entirely. Consider clarifying the recommendation.
- **Outdated line number**: Line reference "around line 1150" for parallel mode is outdated; the actual session handling is around lines 1290-1295 in `_run_parallel()` function.

## Warnings (follow-up ticket)
- **capture_json integration**: The `capture_json` feature writes to logs adjacent to sessions. If `--session` forwarding is removed, verify this doesn't break the feature (covered by pt-buwk testing ticket).
- **Documentation will become inaccurate**: `docs/ralph.md` still describes `--session` forwarding behavior. If pt-ihfv proceeds with removal, this must be updated (pt-oebr covers this).
- **Config options remain defined**: The `sessionDir` and `sessionPerTicket` defaults in `tf_cli/ralph.py:96-97` will become no-ops. Consider deprecation warnings or removal to avoid confusion.
- **Clarify ticket's role**: The ticket claims "No code changes required" but this documentation blocks three implementation tickets. Consider clarifying that the DECISION documented here will drive code changes in dependent tickets.

## Suggestions (follow-up ticket)
- **Add `forwardSession` config option**: If adopting the optional approach, add a `forwardSession: true` config option (defaulting to true for backward compatibility).
- **Document in CHANGELOG**: If this analysis leads to implementation changes, document the `RALPH_FORCE_LEGACY_SESSIONS` becoming a no-op in CHANGELOG.
- **Add deprecation warning**: Consider adding a deprecation warning when `resolve_session_dir()` is called if the decision is to eventually remove session forwarding.
- **Create migration guide**: Create a migration guide for users who rely on predictable session paths for debugging.
- **Cross-reference code locations**: When pt-ihfv implements the removal, ensure both locations (lines 417 and 1758) are updated consistently. Consider adding code comments cross-referencing each other.

## Summary Statistics
- Critical: 1
- Major: 2
- Minor: 2
- Warnings: 4
- Suggestions: 5

## Reviewer Consensus
All reviewers agree the analysis is accurate and well-structured. The primary concern is that the ticket needs to make a **clear, definitive decision** to unblock the dependent implementation tickets (pt-buwk, pt-ihfv, pt-oebr).
