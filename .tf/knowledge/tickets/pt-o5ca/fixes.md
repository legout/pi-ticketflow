# Fixes: pt-o5ca

## Summary
Fixed 4 Critical and 5 Major issues identified in review. The implementation document now correctly handles chain construction, post-chain execution gating, flag conflicts, and artifact path resolution.

## Fixes by Severity

### Critical (must fix)

#### 1. Fixed: Double implement phase when using `--no-research`
- **Issue**: When `--no-research` set entry to `tf-implement`, the chain still included `-> tf-implement ->`, causing duplicate execution
- **Fix**: Added dynamic chain construction:
  ```bash
  if [[ "$research_entry" == "tf-research" ]]; then
      chain="tf-research -> tf-implement -> tf-review -> tf-fix -> tf-close"
  else
      chain="tf-implement -> tf-review -> tf-fix -> tf-close"
  fi
  ```

#### 2. Fixed: Post-chain commands run unconditionally
- **Issue**: Post-chain commands ran regardless of chain success/failure
- **Fix**: Added explicit exit status check:
  ```bash
  pi "/chain-prompts $chain -- $ticket_id"
  chain_status=$?
  if [[ $chain_status -eq 0 ]]; then
      # Run post-chain commands
  else
      echo "Chain completed with status $chain_status..."
      exit $chain_status
  fi
  ```

#### 3. Fixed: Flag conflict resolution undefined
- **Issue**: No behavior specified when both `--no-research` and `--with-research` provided
- **Fix**: Documented "last flag wins" rule with explicit examples

#### 4. Fixed: Post-chain failure handling undefined
- **Issue**: Ambiguous behavior if post-chain command fails
- **Fix**: Specified best-effort policy with warning logs:
  ```bash
  pi "/tf-followups $artifact_dir/review.md" || {
      echo "Warning: tf-followups failed, continuing..." >&2
  }
  ```

### Major (should fix)

#### 5. Fixed: Post-chain commands missing required arguments
- **Issue**: `--create-followups` documented as requiring artifact path, but pseudo-code didn't pass it
- **Fix**: Updated to pass artifact directory:
  ```bash
  pi "/tf-followups $artifact_dir/review.md"
  ```

#### 6. Fixed: Wrapper doesn't respect config for research default
- **Issue**: Wrapper defaulted to `tf-research` regardless of `workflow.enableResearcher`
- **Fix**: Added config-aware behavior documentation and pseudo-code comments

#### 7. Fixed: Quality gate edge case with retry/escalation
- **Issue**: Didn't specify whether post-chain runs after first CLOSED or only on initial success
- **Fix**: Clarified that post-chain runs when chain completes with CLOSED, regardless of retry attempts

#### 8. Fixed: Artifact path assumption for post-chain commands
- **Issue**: Post-chain commands needed deterministic artifact discovery
- **Fix**: Documented convention-based path: `{knowledgeDir}/tickets/{ticket-id}/`

#### 9. Fixed: Silent flag dropping risk
- **Issue**: Unknown flag error handling could silently ignore flags
- **Fix**: Added strict error handling: `echo "Error: Unknown flag: $1" >&2; exit 1`

### Minor (nice to fix)

#### 10. Fixed: Missing ticket_id validation
- **Issue**: No explicit validation for missing/empty `ticket_id`
- **Fix**: Added early validation with usage message

#### 11. Fixed: Execution order rationale missing
- **Issue**: Specified order lacked rationale
- **Fix**: Added explanation for followups → simplify → review-loop ordering

#### 12. Fixed: Migration friction with both extensions installed
- **Issue**: Potential confusion when both extensions installed
- **Fix**: Added "Extension priority" section explaining project-local precedence

## Summary Statistics
- **Critical**: 4 (all fixed)
- **Major**: 5 (all fixed)
- **Minor**: 3 (all fixed)
- **Warnings**: 0
- **Suggestions**: 0

## Verification
- Reviewed updated implementation.md against all review comments
- Verified pseudo-code syntax correctness
- Confirmed all acceptance criteria still met
