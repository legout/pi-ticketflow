# Assumptions

- `interactive_shell` dispatch/background mode is reliable for long-running Pi ticket implementations.
- `pi /tf <ticket-id> --auto` can run unattended once started.
- Ralph’s existing dependency/component gating logic can be reused for parallel scheduling.
- Progress and lessons should remain file-based so loop state survives process/context resets.
