# MVP Scope

## In Scope

- Add `metaModels.fixer` to `.tf/config/settings.json` (repo default settings).
- Update `agents.fixer` to use `fixer`.
- Ensure model resolution logic supports the new key.
- Add/adjust minimal tests (if present) for meta-model resolution.
- Update docs/help text that describe meta-models/agents.

## Out of Scope

- Creating multiple fixer profiles (e.g. `fixer-fast`, `fixer-accurate`).
- Changing reviewer/worker defaults.
