# Constraints: seed-automatic-planning-sessions-linkage

- Must not require introducing a new command (preference: enhance `/tf-seed`).
- Must preserve existing behavior when `--no-session` is used.
- Must support multiple sessions per seed (history + reactivation).
- Must avoid surprising behavior after backlog generation: session should be completed and automatically deactivated.
- Prefer minimal dependencies (stdlib JSON, no database).
- Must handle missing knowledge dir gracefully (create directories as needed).
