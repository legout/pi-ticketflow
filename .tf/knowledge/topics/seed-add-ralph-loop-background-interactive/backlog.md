# Backlog: seed-add-ralph-loop-background-interactive

| ID | Title | Score | Est. Hours | Depends On | Links |
|----|-------|-------|------------|------------|-------|
| pt-6d99 | Define dispatch-default Ralph execution contract | 6 | 1-2 | - | pt-0v53 |
| pt-0v53 | Add per-ticket worktree lifecycle for dispatch runs | 5 | 1-2 | pt-6d99 | pt-6d99,pt-9yjn |
| pt-9yjn | Implement run_ticket_dispatch launcher for Ralph | 3 | 1-2 | pt-0v53 | pt-0v53,pt-7jzy |
| pt-7jzy | Handle dispatch completion and graceful session termination | 3 | 1-2 | pt-9yjn | pt-9yjn,pt-699h |
| pt-699h | Implement parallel dispatch scheduling with component safety | 3 | 1-2 | pt-7jzy | pt-7jzy,pt-8qk8 |
| pt-8qk8 | Implement orphaned session recovery and TTL cleanup | 3 | 1-2 | pt-699h | pt-699h,pt-uu03 |
| pt-uu03 | Run manual validation matrix for dispatch Ralph mode | 1 | 1-2 | pt-8qk8 | pt-8qk8,pt-4eor |
| pt-4eor | Integrate dispatch backend into serial Ralph loop state updates | 0 | 1-2 | pt-uu03 | pt-uu03,pt-zmah |
| pt-zmah | Add dispatch session observability and attach hints | 0 | 1-2 | pt-4eor | pt-4eor |