# Sources

- User request: “show ready and blocked ticket count in tf ralph progressbar instead of the current e.g [1/5]. when using normal logging, show number of ready and blocked tickets in the log when starting/finishing a ticket.”

## Notes

- Candidate implementation likely touches the Ralph scheduler/queue logic and the progress/log formatting layer.
- Prefer deriving counts from Ralph’s in-memory view of ticket state to avoid repeated `tk` queries.

## Session Links

- Plan: [plan-ready-blocked-counts-ralph](topics/plan-ready-blocked-counts-ralph/plan.md)
