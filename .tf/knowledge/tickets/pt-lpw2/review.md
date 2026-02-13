# Review: pt-lpw2

## Critical (must fix)
- `docs/configuration.md:180-181` - Documents that when `metaModels.fixer` is not defined, the fixer agent falls back to using the `general` meta-model. However, `tf/frontmatter.py:41` implements fallback to treating the meta-key as a direct model ID, which would produce an invalid model value ("fixer") and likely fail at runtime. This misrepresentation can lead users to believe their configuration is safe when it would actually break.

## Major (should fix)
- `docs/configuration.md:174` - The Model Strategy table lists the fixer model as `zai-org/GLM-4.7-Flash` (missing provider prefix), while the example configuration uses `chutes/zai-org/GLM-4.7-Flash`. This inconsistency may confuse users about the correct, fully-qualified model identifier.

## Minor (nice to fix)
- The section could explicitly note that the `agents.fixer` mapping is required for the fixer meta-model to take effect.

## Warnings (follow-up ticket)
- No issues found

## Suggestions (follow-up ticket)
- Consider standardizing all path references to `.tf/config/settings.json` (some sections still say `config/settings.json`) to avoid user confusion about the canonical location.

## Summary Statistics
- Critical: 1
- Major: 1
- Minor: 1
- Warnings: 0
- Suggestions: 1
