# Assumptions

- `pi-prompt-template-model` `/chain-prompts` is stable enough to run long multi-step workflows.
- Per-step model/skill/thinking application + restore works reliably, including when a step errors.
- TF phase boundaries can be represented cleanly as prompt templates without losing required context.
- `pi-subagents` remains available for parallel review execution.
