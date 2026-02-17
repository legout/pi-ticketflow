# seed-add-retry-logic-on-failed-tickets

Add retry-aware behavior for tickets that fail to close (e.g., due to the quality gate) — especially in the Ralph loop. The goal is to avoid thrashing on the same ticket and instead converge by escalating to more capable models for review/fix (and optionally implement) based on retry count.

## Keywords
- ralph
- retries
- quality-gate
- failon
- escalation
- model-selection
- workflow
- automation
