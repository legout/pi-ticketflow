# Implementation: pt-zmah

## Summary
Added dispatch session observability to Ralph by enhancing logging in `run_ticket_dispatch()` and completion handling:
- Session ID is now logged prominently with a dedicated "Session started:" message
- Attach/watch instructions are logged: "To attach and watch: pi /attach {session_id}"
- Output capture paths are logged at dispatch start for both file mode and JSON capture mode
- Artifact paths are logged at completion for completed/failed tickets

## Retry Context
- Attempt: 1
- Escalated Models: fixer=base, reviewer-second=base, worker=base

## Files Changed
- `tf/ralph.py` - Added session observability logging:
  - Lines 996-997: Session start and attach instructions logging
  - Lines 1000-1006: Output path logging at dispatch start
  - Lines 2911-2918: Artifact path logging at completion

## Key Decisions
- **Location**: Added observability logging in `run_ticket_dispatch()` right after successful session registration (~line 990)
- **Completion logging**: Added artifact path logging after dispatch completion in the serial loop (~line 2911)
- **Log level**: Used INFO level to ensure visibility in normal mode while keeping concise per constraints
- **Format**: Used structured log messages with path fields for programmatic access
- **Output path handling**: Only log JSON path when logs_dir is available to avoid invalid path construction

## Implementation Details

### Dispatch Start Logging (run_ticket_dispatch)

Three new log statements after a dispatch is successfully launched:

1. **Session started**: `log.info(f"Session started: {session_id}", ticket=ticket, session_id=session_id)`
2. **Attach instructions**: `log.info(f"To attach and watch: pi /attach {session_id}", ticket=ticket, session_id=session_id)`
3. **Output path** (conditional):
   - For `pi_output=file`: logs the log file path
   - For `capture_json`: logs the JSONL output path (when logs_dir available)

Example output:
```
2026-02-14T03:30:00Z INFO | ticket=pt-zmah | Dispatching: pi -p "/tf pt-zmah --auto" (session: abc123...)
2026-02-14T03:30:01Z INFO | ticket=pt-zmah | Dispatch launched with PID: 12345
2026-02-14T03:30:01Z INFO | ticket=pt-zmah | session_id=abc123 | Session started: abc123
2026-02-14T03:30:01Z INFO | ticket=pt-zmah | session_id=abc123 | To attach and watch: pi /attach abc123
2026-02-14T03:30:01Z INFO | ticket=pt-zmah | log_path=/path/to/.tf/ralph/logs/pt-zmah.log | Output will be captured at: /path/to/.tf/ralph/logs/pt-zmah.log
```

### Completion Artifact Logging (serial loop)

After dispatch completion, logs artifact paths for access:

```python
ticket_logger.info(
    f"Session artifacts: log={log_file}, json={json_file}",
    ticket=ticket,
    log_path=str(log_file),
    json_path=str(json_file),
    session_id=dispatch_result.session_id,
)
```

Example output:
```
2026-02-14T03:35:00Z INFO | ticket=pt-zmah | session_id=abc123 | Session artifacts: log=/path/.tf/ralph/logs/pt-zmah.log, json=/path/.tf/ralph/logs/pt-zmah.jsonl
```

## Tests Run
- Syntax check: `python3 -c "import ast; ast.parse(open('tf/ralph.py').read())"` - PASS
- Import check: `python3 -c "from tf.ralph import run_ticket_dispatch; print('Import OK')"` - PASS

## Verification
To verify the implementation works:
1. Run a ticket in dispatch mode: `tf ralph run pt-XXXX`
2. Check log output for:
   - "Session started:" message with session ID
   - "To attach and watch: pi /attach {session_id}" instruction
   - Output path (when using `--pi-output file` or `--capture-json`)
3. Wait for completion and check for:
   - "Session artifacts:" message with log and JSON paths
4. The session ID should be copy-paste ready for attaching
