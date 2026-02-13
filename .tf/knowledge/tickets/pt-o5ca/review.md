# Review: pt-o5ca

## Critical (must fix)

### 1. Double implement phase when using `--no-research`
- **Location**: `implementation.md` pseudo-code section
- **Issue**: When `--no-research` is set, `research_entry` becomes `tf-implement`, but the chain still includes `-> tf-implement ->`, causing implement to run twice
- **Fix**: The chain should be constructed dynamically based on entry point:
  - If entry is `tf-research`: chain is `tf-research -> tf-implement -> tf-review -> tf-fix -> tf-close`
  - If entry is `tf-implement`: chain is `tf-implement -> tf-review -> tf-fix -> tf-close` (no repeat)

### 2. Post-chain commands run unconditionally (not gated on chain success)
- **Location**: `implementation.md` lines 85-91
- **Issue**: Post-chain commands run regardless of chain success/failure status, contradicting the documented quality gate behavior
- **Fix**: Check chain exit status before running post-chain commands; only run if chain returned CLOSED status

### 3. Flag conflict resolution undefined
- **Location**: `implementation.md` flag parsing section
- **Issue**: No behavior specified when both `--no-research` and `--with-research` are provided
- **Fix**: Document precedence rule (e.g., "last flag wins" or "conflicting flags produce an error")

### 4. Post-chain failure handling undefined
- **Location**: `implementation.md` lines 120-130
- **Issue**: If a post-chain command (e.g., `tf-followups`) fails, overall workflow status is ambiguous
- **Fix**: Specify behavior: (a) fail the ticket, (b) warn and continue, or (c) require manual cleanup

## Major (should fix)

### 5. Post-chain commands missing required arguments
- **Location**: `implementation.md` lines 49, 77, 89-90
- **Issue**: `--create-followups` is documented as requiring artifact path argument, but pseudo-code doesn't pass it
- **Fix**: Update pseudo-code to pass artifact directory: `pi "/tf-followups {artifact_dir}/review.md"`

### 6. Wrapper doesn't respect config for research default
- **Location**: `implementation.md` lines 70, 161
- **Issue**: Wrapper defaults to `tf-research` regardless of `workflow.enableResearcher` config setting
- **Fix**: Add config-aware branching: check `workflow.enableResearcher` to determine default entry point

### 7. Quality gate edge case with retry/escalation
- **Location**: `implementation.md` lines 101-106
- **Issue**: Doesn't specify whether post-chain runs after first CLOSED or only on initial success (with retries)
- **Fix**: Clarify that post-chain runs only when chain completes with CLOSED status, regardless of retry attempts

### 8. Artifact path assumption for post-chain commands
- **Location**: `implementation.md` lines 141-145
- **Issue**: Post-chain commands need deterministic artifact discovery without explicit file passing in chain-prompts
- **Fix**: Document how artifact directory is conveyed (e.g., via environment variable or convention)

### 9. Silent flag dropping risk
- **Location**: `implementation.md` line 88
- **Issue**: Unknown flag error handling may silently ignore flags in certain shell contexts
- **Fix**: Specify strict error handling with explicit `exit 1` and non-zero status

## Minor (nice to fix)

### 10. Missing ticket_id validation
- **Location**: `implementation.md` lines 65-67, 86
- **Issue**: No explicit validation for missing/empty `ticket_id`
- **Fix**: Add early validation with usage error message

### 11. Execution order rationale missing
- **Location**: `implementation.md` line 54
- **Issue**: Specified order (followups → simplify → review-loop) lacks rationale
- **Fix**: Explain why simplification happens after followup creation (or reverse if appropriate)

### 12. Migration friction with both extensions installed
- **Location**: `implementation.md` lines 166-170
- **Issue**: Users may accidentally invoke `/tf` from wrong extension when both are installed
- **Fix**: Suggest explicit extension priority documentation

## Warnings (follow-up ticket)

### 13. Interrupt handling during post-chain
- **Location**: `implementation.md` lines 131-135
- **Issue**: Ctrl+C during post-chain may leave ticket in ambiguous state
- **Follow-up**: Implement post-chain idempotency or recovery mechanism

### 14. Entry point model divergence
- **Location**: `implementation.md` line 44
- **Issue**: Different entry models (`kimi-coding/k2p5` vs `minimax/MiniMax-M2.5`) may surprise users
- **Follow-up**: Document that research model context doesn't carry over when skipping research

## Suggestions (follow-up ticket)

### 15. Flag validation preflight
- **Location**: `implementation.md` line 185
- **Suggestion**: Validate all flags are known and compatible before starting chain
- **Benefit**: Prevents wasting compute on multi-phase chain only to fail on unknown flag

### 16. Telemetry/logging hook point
- **Location**: `implementation.md` lines 200-210
- **Suggestion**: Add extension point for logging flag usage
- **Benefit**: Helps identify most-used flags for future UX optimization

## Summary Statistics
- **Critical**: 4
- **Major**: 5
- **Minor**: 3
- **Warnings**: 2
- **Suggestions**: 2
