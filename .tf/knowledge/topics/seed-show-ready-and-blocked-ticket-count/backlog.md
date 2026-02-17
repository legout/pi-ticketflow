# Backlog: seed-show-ready-and-blocked-ticket-count

| ID | Title | Score | Est. Hours | Depends On | Links |
|----|-------|-------|------------|------------|-------|
| pt-m54d | Define Ralph ready/blocked semantics + output contract | 6 | 1-2 | - | pt-oa8n |
| pt-oa8n | Implement queue-state snapshot helper (ready/blocked/running/done) | 3 | 1-2 | pt-m54d | pt-m54d,pt-ri6k |
| pt-ussr | Update Ralph progress display to show ready/blocked counts | 0 | 1-2 | pt-oa8n | pt-ri6k,pt-g6be |
| pt-g6be | Add ready/blocked counts to normal Ralph logging (ticket start/finish) | 0 | 1-2 | pt-ussr | pt-ussr |
| pt-ri6k | Add tests for queue-state counts + progress/log formatting | 1 | 1-2 | pt-g6be | pt-oa8n,pt-ussr |
