# Backlog: plan-auto-planning-sessions-linkage
| ID | Title | Score | Est. Hours | Depends On | Links |
|----|-------|-------|------------|------------|-------|
| pt-g53y | Define planning session schema + atomic JSON store | 9 | 1-2 | - | - |
| pt-cqbn | Implement /tf-seed session activation + archive+switch + --no-session | 3 | 1-2 | pt-g53y | - |
| pt-9zhm | Add /tf-seed session UX: --active, --sessions, --resume | 0 | 1-2 | pt-cqbn | - |
| pt-v2jv | Implement session-aware /tf-spike auto-linking | 3 | 1-2 | pt-9zhm | - |
| pt-7l5c | Implement session-aware /tf-plan attachment + Inputs/Related Topics | 3 | 1-2 | pt-v2jv | - |
| pt-jpyf | Implement session finalization in /tf-backlog (record + complete + deactivate) | 3 | 1-2 | pt-7l5c | - |
| pt-qdp1 | Update prompts/docs to document planning sessions | 0 | 1-2 | pt-jpyf | - |
| pt-x2v0 | Test planning session lifecycle + idempotency | 1 | 1-2 | pt-qdp1 | - |
