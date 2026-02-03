---
description: Print the next open and ready ticket id
model: zai/glm-4.7
thinking: medium
---

# /tf-next

Return the logical next open and ready ticket id.

## Execution

1. If `.tf/ralph/config.json` exists and contains `ticketQuery`, use it.
   - Otherwise use: `tk ready | head -1 | awk '{print $1}'`.
2. Run the command via `bash`.
3. Print only the ticket id. If no ticket is found, say "No ready tickets found.".
