# Research: pt-tl00

## Status
Research enabled. Minimal external research was performed - this is an internal feature implementation.

## Context Reviewed
- Ticket pt-tl00: Ralph integration for retry capping
- Plan: plan-retry-logic-quality-gate-blocked (approved)
- Current Ralph implementation: tf/ralph.py, tf/ralph/__init__.py, tf/ralph/queue_state.py
- Current config: .tf/config/settings.json

## Key Findings

### Existing Infrastructure
1. **Retry state format**: Already defined in skill (retry-state.json schema version 1)
2. **Escalation config**: Present in settings.json but disabled (`enabled: false`)
3. **Detection algorithm**: Defined in tf-workflow skill for parsing close-summary.md
4. **Progress tracking**: Ralph already updates .tf/ralph/progress.md via update_state()

### Implementation Points
1. Ralph needs to:
   - Check retry-state.json before selecting a ticket
   - Skip tickets with retryCount >= maxRetries
   - Record retry attempt counts in progress.md
   - Warn when parallelWorkers > 1 (no locking)

2. The retry state location:
   - `{knowledgeDir}/tickets/{ticket-id}/retry-state.json`
   - Default: `.tf/knowledge/tickets/{ticket-id}/retry-state.json`

### Code Locations
- Ticket selection: `select_ticket()` in tf/ralph.py
- Progress updates: `update_state()` in tf/ralph.py
- Main loop: `ralph_start()` serial mode section
- Config loading: `load_config()` and settings.json

## Sources
- .tf/knowledge/topics/plan-retry-logic-quality-gate-blocked/plan.md
- tf/ralph.py (main Ralph implementation)
- .tf/config/settings.json
