# Backlog: seed-add-retry-logic-on-failed-tickets

| ID | Title | Score | Est. Hours | Depends On | Links |
|----|-------|-------|------------|------------|-------|
| pt-te9b | Define retry state + quality-gate block detection | 6 | 1-2 | - | pt-xu9u |
| pt-xu9u | Implement retry-aware escalation in /tf workflow | 3 | 1-2 | pt-te9b | pt-te9b,pt-7lrp |
| pt-7lrp | Tests + docs for retries and escalation | 1 | 1-2 | pt-xu9u | pt-xu9u,pt-lbvu |
| pt-lbvu | Add escalation config to settings (workflow.escalation) | 0 | 1-2 | pt-7lrp | pt-7lrp,pt-9uxj |
| pt-9uxj | Make quality gate meaningful: post-fix re-review before close | 0 | 1-2 | pt-lbvu | pt-lbvu,pt-tl00 |
| pt-tl00 | Ralph integration: cap retries and stop thrashing on blocked tickets | 0 | 1-2 | pt-9uxj | pt-9uxj |