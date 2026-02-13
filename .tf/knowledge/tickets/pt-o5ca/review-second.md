# Review: pt-o5ca

## Overall Assessment
The hybrid flag strategy is sound and well-documented. However, several edge cases around flag interactions, post-chain error handling, and artifact lifecycle could create subtle failures in production use. The document is documentation-only with no executable code, so risks are primarily in specification gaps that may lead to implementation bugs.

## Critical (must fix)
- `implementation.md:79-86` - **Undefined flag conflict resolution**: No behavior specified when both `--no-research` and `--with-research` are provided simultaneously. The pseudo-code shows independent case statements that would allow both, creating undefined entry point behavior. Specify precedence (last-flag-wins or error) before implementation.

- `implementation.md:120-130` - **Post-chain failure handling undefined**: If `tf-followups` or `simplify-tickets` fails after the main chain succeeds, the overall workflow status is ambiguous. Specify whether partial post-chain failures should: (a) fail the ticket, (b) warn and continue, or (c) require manual cleanup.

## Major (should fix)
- `implementation.md:101-106` - **Quality gate edge case incompletely specified**: States "post-chain commands only run if chain completes (CLOSED status)" but doesn't address retry/escalation scenarios where chain may complete with CLOSED after multiple attempts. Clarify whether post-chain runs after first CLOSED or only on initial success.

- `implementation.md:141-145` - **Artifact path assumption for post-chain commands**: `/tf-followups <artifact-dir>/review.md` assumes `artifact-dir` is known and populated. In a pure chain-prompts flow without explicit file passing, the post-chain wrapper needs deterministic artifact discovery logic. Document how `$ARTIFACT_DIR` or similar is conveyed to post-chain commands.

- `implementation.md:88` - **Silent flag dropping risk**: Unknown flags echo error but exit code handling isn't specified. Implementation may silently ignore unknown flags in certain shell contexts (set +e). Specify strict error handling: `exit 1` with non-zero status for unknown flags.

## Minor (nice to fix)
- `implementation.md:54` - **Execution order rationale missing**: The specified order (followups → simplify → review-loop) should include rationale. Why should simplification happen after followup creation? Intuitively, simplifying first might yield cleaner followup tickets.

- `implementation.md:166-170` - **Migration friction underestimated**: States "Remove `pi-model-switch` (optional - can keep for other workflows)" but doesn't address potential confusion when both extensions are installed. Users may accidentally invoke `/tf` from the wrong extension. Suggest explicit extension priority documentation.

## Warnings (follow-up ticket)
- `implementation.md:131-135` - **Interrupt handling during post-chain**: If user interrupts (Ctrl+C) during post-chain commands, the ticket may be left in an ambiguous state (chain closed, post-chain partial). Suggest implementing post-chain idempotency or a recovery mechanism.

- `implementation.md:44` - **Entry point model configuration divergence**: `/tf-research` uses `kimi-coding/k2p5` while `/tf-implement` uses `minimax/MiniMax-M2.5`. If research is skipped, the implement phase starts "cold" without the research model's context. This is architecturally correct but may surprise users expecting consistent entry behavior.

## Suggestions (follow-up ticket)
- `implementation.md:185` - **Consider flag validation preflight**: Before starting the chain, validate all flags are known and compatible. This prevents wasting compute on a 5-phase chain only to fail on an unknown post-chain flag.

- `implementation.md:200-210` - **Add telemetry/logging hook point**: The wrapper implementation could benefit from an extension point for logging flag usage, helping identify which flags are most used for future UX optimization.

## Positive Notes
- The hybrid approach elegantly avoids the combinatorial explosion problem (2^n chains) that would plague a pure chain-variant approach
- Backward compatibility story is thorough and acknowledges the importance of preserving muscle memory for existing users
- The separation of research control (entry point) from post-processing (wrapper) shows clear architectural thinking
- Quality gate integration preserves existing failure semantics - a good conservative default

## Summary Statistics
- Critical: 2
- Major: 3
- Minor: 2
- Warnings: 2
- Suggestions: 2
