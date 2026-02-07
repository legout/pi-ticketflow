# Backlog: plan-kb-management-cli
| ID | Title | Score | Est. Hours | Depends On | Links |
|----|-------|-------|------------|------------|-------|
| pt-6rja | Add Python CLI dispatch for tf kb (bypass legacy) | 0 | 1-2 | - | - |
| pt-fsk3 | Implement kb helpers: knowledgeDir resolve + atomic index.json IO | 3 | 1-2 | pt-6rja | - |
| pt-1pxe | Implement tf kb ls + show | 3 | 1-2 | pt-fsk3 | - |
| pt-74c7 | Implement tf kb archive + restore | 3 | 1-2 | pt-1pxe | - |
| pt-paih | Implement tf kb delete (permanent) + index cleanup | 3 | 1-2 | pt-74c7 | - |
| pt-3nit | Implement tf kb validate | 3 | 1-2 | pt-paih | - |
| pt-6q53 | Implement tf kb rebuild-index (--dry-run) | 3 | 1-2 | pt-3nit | - |
| pt-7gmp | Add tests + docs for tf kb | 0 | 1-2 | pt-6q53 | - |
