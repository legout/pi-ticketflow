# Constraints

- Keep the user-facing contract: `/tf <ticket-id>` should remain the standard entry point (or provide a backward-compatible alias).
- Preserve the existing artifact policy and directories under `.tf/knowledge/`.
- Avoid a proliferation of duplicated logic across prompts; shared logic should remain in reusable Python modules or a shared skill.
- Must work in non-interactive mode (`pi -p`) for scripting / automation.
