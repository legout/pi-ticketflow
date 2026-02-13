# Review: pt-o5ca

## Overall Assessment
The hybrid strategy is a strong direction and the document is clear, but the pseudo-implementation has several correctness gaps that would cause wrong runtime behavior if implemented as written. The highest-risk issues are around phase sequencing and post-chain execution semantics, which currently conflict with the intended workflow guarantees. These should be resolved in the design doc before downstream implementation tickets proceed.

## Critical (must fix)
- `.tf/knowledge/tickets/pt-o5ca/implementation.md:75-76,86` - With `--no-research`, `research_entry` is set to `tf-implement`, but the chain still explicitly includes `-> tf-implement -> ...`, so implement would run twice. This breaks the intended phase order and can cause duplicate edits/artifacts.
- `.tf/knowledge/tickets/pt-o5ca/implementation.md:85-91,203-206` - The pseudo-code runs post-chain commands unconditionally after invoking the chain and does not gate them on successful close status. That contradicts the stated quality-gate behavior and can trigger follow-up actions on failed/BLOCKED tickets.

## Major (should fix)
- `.tf/knowledge/tickets/pt-o5ca/implementation.md:49,77,89-90` - `--create-followups` is documented as `/tf-followups <artifact-dir>/review.md`, but pseudo-code only stores `"tf-followups"` and executes `pi "/$cmd"` without required arguments. This would fail or produce non-deterministic artifact selection.
- `.tf/knowledge/tickets/pt-o5ca/implementation.md:70,161` - The wrapper defaults to `tf-research` regardless of config, while the doc claims default behavior remains "research runs if enabled in config." Without explicit config-aware branching, behavior changes when research is disabled.

## Minor (nice to fix)
- `.tf/knowledge/tickets/pt-o5ca/implementation.md:65-67,86` - No explicit validation for missing/empty `ticket_id` is shown. Failing fast with a usage error would prevent ambiguous chain invocations and simplify troubleshooting.

## Warnings (follow-up ticket)
- `.tf/knowledge/tickets/pt-o5ca/implementation.md:73-81` - Flag conflict handling (e.g., both `--no-research` and `--with-research`) is implicit rather than specified. Documenting precedence now avoids inconsistent behavior across shell or Python wrapper implementations.

## Suggestions (follow-up ticket)
- `.tf/knowledge/tickets/pt-o5ca/implementation.md:53-57` - Add explicit rationale for post-chain execution order and failure policy per command (stop-on-first-failure vs best-effort). This improves maintainability and testability for future optional flags.

## Positive Notes
- The chosen hybrid model is sensible and avoids combinatorial chain explosion.
- Flag mapping is presented clearly with examples, making the design easy to implement.
- Backward compatibility and migration concerns are explicitly documented.

## Summary Statistics
- Critical: 2
- Major: 2
- Minor: 1
- Warnings: 1
- Suggestions: 1
