# Sources

## Local Files

- `.tf/config/settings.json`

## Notes

- Follow the existing model-switch pattern: `prompts.<command>` → meta-model key → `metaModels.<key>.model`.
- Ensure `agents.fixer` points at a meta-model key that exists (or is handled via fallback).
