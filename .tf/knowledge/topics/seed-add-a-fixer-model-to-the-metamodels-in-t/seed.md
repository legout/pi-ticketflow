# Seed: add a fixer model to the metamodels in the settings

## Vision

Make the IRF **Fix** step use a purpose-chosen model (e.g., cheaper/faster for small fixes or stronger for tricky patches) without affecting planning/review/general tasks.

## Core Concept

Introduce a `metaModels.fixer` entry in `.tf/config/settings.json` and wire `agents.fixer` to that meta-model key. Keep current behavior as default/fallback.

## Key Features

1. Add a `fixer` meta-model key under `metaModels` (model + thinking + description)
2. Point `agents.fixer` to `fixer` (or add clear fallback behavior)
3. Ensure `/tf` model switching resolves the new meta-model consistently

## Open Questions

- Should `fixer` default to the same model as `general` when missing (backward compatible), or should it be required?
- Should escalation config (`workflow.escalation.models.fixer`) override `agents.fixer`, or vice versa?
