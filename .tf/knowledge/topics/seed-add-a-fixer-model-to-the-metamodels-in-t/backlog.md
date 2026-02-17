# Backlog: seed-add-a-fixer-model-to-the-metamodels-in-t

| ID | Title | Score | Est. Hours | Depends On | Links |
|----|-------|-------|------------|------------|-------|
| pt-g2tu | Add metaModels.fixer and map agents.fixer to it in settings.json | 10 | 1-2 | - | pt-lpw2 |
| pt-lpw2 | Update docs/help text to mention metaModels.fixer | 8 | 1-2 | pt-g2tu | pt-g2tu,pt-lw9p |
| pt-lw9p | Define fixer meta-model selection rules (fallback + escalation) | 7 | 1-2 | pt-lpw2 | pt-lpw2,pt-6zp2 |
| pt-6zp2 | Add tests for fixer meta-model selection + backward compatibility | 4 | 1-2 | pt-lw9p | pt-lw9p,pt-u9cj |
| pt-u9cj | Implement fixer meta-model resolution (use fixer key with safe fallback) | 3 | 1-2 | pt-6zp2 | pt-6zp2 |