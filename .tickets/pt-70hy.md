---
id: pt-70hy
status: closed
deps: [pt-qayw]
links: [pt-7i3q]
created: 2026-02-07T14:17:18Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-ticket-title-in-the-logging-when-run
tags: [tf, backlog, component:tests, component:workflow]
---
# Cache ticket title lookups in Ralph to avoid repeated tk calls

## Task
Implement caching for ticket title lookups in Ralph loop to avoid calling tk show repeatedly for the same ticket.

## Context
tf ralph processes tickets in a loop, and the same ticket may be referenced multiple times. The extract_ticket_title() function already exists but makes a subprocess call each time. We need to cache results per ticket during a run.

## Acceptance Criteria
- [ ] Ticket title cache implemented (dict: ticket_id -> title)
- [ ] Cache is populated on first lookup and reused
- [ ] Cache is cleared or refreshed appropriately between runs
- [ ] No regression in performance

## Constraints
- Avoid adding network calls or heavy I/O
- Keep cache simple (in-memory dict)

## References
- Seed: seed-add-ticket-title-in-the-logging-when-run


## Notes

**2026-02-07T17:02:43Z**

**Completed** ✅

**Implementation Summary:**
Implemented ticket title caching in Ralph to avoid repeated  subprocess calls. The cache is a module-level dict that stores ticket_id -> title mappings, cleared at the start of each Ralph run.

**Changes:**
- Added  module-level cache
- Added  function
- Modified  to use cache with  parameter
- Fixed duplicate type annotation in 
- Cache cleared at start of  and 

**Review:**
- Critical: 0 (fixed 1)
- Major: 0 (fixed 1)  
- Minor: 3 (1 fixed, 2 deferred)
- All 693 tests pass

**Commit:** f69103d

**Artifacts:** 
