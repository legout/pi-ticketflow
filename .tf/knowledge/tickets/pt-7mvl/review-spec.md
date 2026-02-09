# Review (Spec Audit): pt-7mvl

## Overall Assessment
The implementation.md provides thorough documentation of the current `--session` forwarding behavior and analyzes the implications of its removal. However, this ticket is a research/analysis ticket with no actual code changes. The analysis is well-structured but contains a critical gap: it recommends proceeding with caution and even suggests an alternative approach (making `--session` optional via config), which contradicts the seed's directive to remove it entirely. The ticket is marked complete but doesn't definitively decide the path forward for the dependent implementation ticket (pt-ihfv).

## Critical (must fix)
- `tf_cli/ralph.py:417` - The `--session` forwarding code is still present in the codebase, which contradicts the seed's requirement. The implementation.md states "No code changes required for this ticket" but this is a research/definition ticket - the actual removal should be tracked as incomplete work for ticket pt-ihfv. The acceptance criteria claim this is "documented above" but the ticket's scope was to define behavior, not implement it. The dependent ticket pt-ihfv ("Remove pi --session forwarding") is blocked by pt-buwk (tests), which depends on this ticket's decision. The analysis concludes with "Proceed with caution" and suggests an alternative approach, creating ambiguity for the implementation ticket.

## Major (should fix)
- `implementation.md:1` - The implementation document lacks a clear "Decision" section that definitively states: (1) whether to proceed with removal or the optional-config approach, (2) what the source of truth for session selection will be (Pi's internal defaults vs. Ralph's config), and (3) explicit guidance for pt-ihfv implementers. The current "Recommendation" section leaves the decision open-ended.
- `implementation.md:170-175` - The alternative approach (making `--session` optional via `forwardSession: false` config) is presented but not evaluated against the seed's acceptance criteria. The seed explicitly asks for removal, not optionality.

## Minor (nice to fix)
- `implementation.md:45-46` - Line numbers for parallel mode execution loop reference "around line 1150" but the actual parallel session handling is around lines 1290-1295 in `_run_parallel()` function. The line number is outdated.

## Warnings (follow-up ticket)
- `docs/ralph.md:87,114-126` - Documentation still describes the `--session` forwarding behavior including `sessionDir` and `sessionPerTicket` config options. If pt-ihfv proceeds with removal, this documentation will become inaccurate and must be updated (pt-oebr covers this but should verify these specific sections).
- `tf_cli/ralph.py:96-97` - The `sessionDir` and `sessionPerTicket` defaults are still defined. If these become no-ops as suggested in the analysis, they should be deprecated and eventually removed to avoid confusion.

## Suggestions (follow-up ticket)
- `tf_cli/ralph.py:647-710` - Consider adding a deprecation warning when `resolve_session_dir()` is called if the decision is to eventually remove session forwarding. This gives users advance notice of behavioral changes.
- Create a migration guide for users who currently rely on predictable session paths for debugging. The analysis correctly identifies this as a loss of functionality but doesn't propose user-facing migration steps.

## Positive Notes
- The analysis correctly identifies all locations where `--session` is forwarded (lines 381, 407, 411, 417)
- The impact assessment table (lines 90-96) clearly articulates the trade-offs of removing `--session`
- Backward compatibility constraints are thoroughly documented including config options, CLI, and artifact implications
- The relationship between this ticket and dependent tickets (pt-buwk, pt-ihfv, pt-oebr) is correctly mapped in the backlog.md

## Summary Statistics
- Critical: 1
- Major: 2
- Minor: 1
- Warnings: 2
- Suggestions: 2

## Spec Coverage
- Spec/plan sources consulted:
  - `.tf/knowledge/topics/seed-remove-session-param-from-ralph/seed.md`
  - `.tf/knowledge/topics/seed-remove-session-param-from-ralph/overview.md`
  - `.tf/knowledge/topics/seed-remove-session-param-from-ralph/backlog.md`
  - `docs/ralph.md` (current behavior documentation)
  - `tf_cli/ralph.py` (actual implementation)
- Missing specs: None - all relevant spec documents were consulted
