# Success Metrics

- Fewer required Pi extensions for the TF workflow (remove `pi-model-switch` from the required set).
- `/tf <ticket>` still completes the full IRF workflow with correct model selection per phase.
- Phase models and thinking levels are deterministic and visible (via prompt frontmatter + chain execution).
- No regression in artifacts produced (`research.md`, `implementation.md`, `review.md`, `fixes.md`, `close-summary.md`).
- Setup experience improved: fewer installation steps, fewer “missing tool” failure modes.
