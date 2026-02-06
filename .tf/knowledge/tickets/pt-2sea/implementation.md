# Implementation: pt-2sea

## Summary
Implemented lifecycle logging for parallel Ralph mode with batch selection logging (ticket IDs + component tags), worktree operation logging (add/remove with success/failure), and per-ticket exit code and artifact root tracking.

## Files Changed
- `tf_cli/logger.py` - Added `log_batch_selected()` and `log_worktree_operation()` methods
- `tf_cli/ralph_new.py` - Updated parallel mode to use new logging methods

## Key Changes

### 1. New Logger Methods (`tf_cli/logger.py`)

Added 2 new lifecycle logging methods to `RalphLogger`:

- `log_batch_selected(tickets, component_tags, reason, mode, iteration)` - Logs selected batch with ticket IDs and their component tags
  - Shows which tickets were selected and why (component_diversity or fallback)
  - Displays component tags for each ticket (or "untagged" if none)
  - Includes structured context for machine parsing

- `log_worktree_operation(ticket_id, operation, worktree_path, success, error, mode, iteration)` - Logs worktree add/remove operations
  - Tracks both success and failure cases
  - Captures error messages on failure
  - Logs the worktree path for debugging

### 2. Ralph Loop Updates (`tf_cli/ralph_new.py`)

Updated parallel mode in `ralph_start()`:

1. **Batch Selection Logging**: After selecting tickets for parallel processing, logs the batch with component tags using `log_batch_selected()`
   - Distinguishes between "component_diversity" (normal selection) and "fallback" (when no parallelizable tickets found)
   - Shows component tags for each ticket or "untagged" if none

2. **Worktree Add Logging**: Logs worktree add attempts with success/failure status
   - Success: Logs worktree path
   - Failure: Logs error message from git stderr

3. **Worktree Remove Logging**: Logs worktree removal after ticket completion
   - Success: Clean removal
   - Failure: Logs error and falls back to shutil.rmtree

4. **Per-ticket Exit Code**: Already logged via `log_command_executed()` (from pt-ljos)

5. **Artifact Root**: Already logged via `log_error_summary()` with artifact_path (from pt-ljos)

## Acceptance Criteria Verification

| Criteria | Status | Implementation |
|----------|--------|----------------|
| Logs selected batch with ticket IDs + component tags | ✅ | `log_batch_selected()` shows tickets and their components (or "untagged") |
| Logs worktree add/remove operations | ✅ | `log_worktree_operation()` logs both add and remove with success/failure |
| Logs per-ticket exit code | ✅ | `log_command_executed()` already in place from pt-ljos |
| Logs artifact root used | ✅ | `log_error_summary()` includes artifact_path; update_state uses artifact_root |

## Log Output Examples

```
# Batch selected (component diversity)
2026-02-06T18:06:10Z | INFO | TEST-1_components=['component:cli'] | TEST-2_components=['untagged'] | event=batch_selected | iteration=0 | mode=parallel | reason=component_diversity | ticket_count=2 | tickets="['TEST-1', 'TEST-2']" | Selected batch: TEST-1(component:cli), TEST-2(untagged)

# Batch selected (fallback)
2026-02-06T18:06:10Z | INFO | TEST-3_components=['untagged'] | event=batch_selected | iteration=1 | mode=parallel | reason=fallback | ticket_count=1 | tickets="['TEST-3']" | Selected batch: TEST-3(untagged)

# Worktree add success
2026-02-06T18:06:10Z | INFO | event=worktree_operation | iteration=0 | mode=parallel | operation=add | success=True | ticket=TEST-1 | worktree_path=/tmp/worktree/TEST-1 | Worktree add success: /tmp/worktree/TEST-1

# Worktree add failure
2026-02-06T18:06:10Z | ERROR | error="fatal: invalid reference: HEAD" | event=worktree_operation | iteration=0 | mode=parallel | operation=add | success=False | ticket=TEST-2 | worktree_path=/tmp/worktree/TEST-2 | Worktree add failed: /tmp/worktree/TEST-2 - fatal: invalid reference: HEAD

# Worktree remove success
2026-02-06T18:06:10Z | INFO | event=worktree_operation | iteration=0 | mode=parallel | operation=remove | success=True | ticket=TEST-1 | worktree_path=/tmp/worktree/TEST-1 | Worktree remove success: /tmp/worktree/TEST-1

# Worktree remove failure (with fallback cleanup)
2026-02-06T18:06:10Z | ERROR | error="error: failed to remove '/tmp/worktree/TEST-2'" | event=worktree_operation | iteration=0 | mode=parallel | operation=remove | success=False | ticket=TEST-2 | worktree_path=/tmp/worktree/TEST-2 | Worktree remove failed: /tmp/worktree/TEST-2 - error: failed to remove '/tmp/worktree/TEST-2'
```

## Design Decisions

1. **Component Tag Display**: When a ticket has no component tags and `allow_untagged=true`, it displays as "untagged" in logs for clarity.

2. **Worktree Pre-cleanup**: The existing code removes worktrees before adding them (to handle stale worktrees). Now we log successful pre-cleanup removals at debug level implicitly (only failures would be notable).

3. **Error Capture**: Worktree add/remove errors capture the stderr output from git commands for detailed diagnostics.

4. **Conciseness**: Normal operation logs are concise; errors include full details. This follows the constraint to avoid overly chatty logs when many tickets are processed.

## Tests Run

- Verified logger imports correctly
- Verified `log_batch_selected()` produces correct output with component tags
- Verified `log_batch_selected()` handles untagged tickets correctly
- Verified `log_worktree_operation()` logs success cases correctly
- Verified `log_worktree_operation()` logs failure cases with error messages
- Verified ralph_new module imports correctly
- Verified parallel mode code path is syntactically correct
