# Research: pt-7mvl - Define Ralph session behavior without forwarding pi --session

## Status
Research completed. Analysis based on codebase review.

## Context Reviewed

### 1. Current `--session` Usage in Ralph

The `--session` parameter is forwarded to `pi` in two locations in `tf_cli/ralph.py`:

**Location 1: `run_ticket()` function (line ~360)**
```python
session_flag = f" --session {session_path}" if session_path else ""
# ...
args = ["pi", "-p"]
if capture_json:
    args.append("--mode")
    args.append("json")
if session_path:
    args += ["--session", str(session_path)]
args.append(cmd)
```

**Location 2: Parallel mode loop (line ~1150)**
```python
session_path = None
if session_dir:
    session_path = session_dir / f"{ticket}.jsonl"
# ...
args = ["pi", "-p"]
if capture_json:
    args.append("--mode")
    args.append("json")
if session_path:
    args += ["--session", str(session_path)]
args.append(cmd)
```

### 2. Session Directory Resolution

The `resolve_session_dir()` function determines where sessions are stored:

- **Default**: `~/.pi/agent/sessions` (Pi's standard session directory)
- **Legacy**: `.tf/ralph/sessions` (deprecated, emits warning if exists)
- **Config override**: `sessionDir` in `.tf/ralph/config.json`
- **Environment**: `RALPH_FORCE_LEGACY_SESSIONS=1` to force legacy path

### 3. Session-Related Configuration

From `DEFAULTS` in `ralph.py`:
```python
"sessionDir": "~/.pi/agent/sessions",
"sessionPerTicket": True,
```

Behavior:
- `sessionPerTicket=True`: Each ticket gets its own session file (`{ticket}.jsonl`)
- `sessionPerTicket=False`: One session file per loop (`loop-{timestamp}.jsonl`)

### 4. What `--session` Affects

1. **Artifacts**: Pi session logs (JSONL format) for conversation replay/debugging
2. **Resume behavior**: Sessions can theoretically be resumed (though Ralph doesn't use this)
3. **Isolation**: Per-ticket sessions prevent conversation bleed between tickets

### 5. Dependencies

This ticket blocks:
- `pt-buwk`: Add regression test/smoke coverage for ralph pi invocation args
- `pt-ihfv`: Remove pi --session forwarding from tf ralph start/run
- `pt-oebr`: Update tf ralph docs/help text to remove pi --session mention

## Analysis

### Why was `--session` being passed?

1. **Explicit control**: Ralph wanted to control where session files were stored
2. **Per-ticket naming**: To ensure each ticket had a predictable session file path
3. **Isolation**: To prevent conversation history from bleeding between tickets

### What happens if `--session` is removed?

If `--session` is not forwarded to `pi`:
- Pi will use its own default session behavior
- Session files will be stored in Pi's default location (likely `~/.pi/agent/sessions/` with auto-generated names)
- Ralph loses control over session file naming
- Session files may be harder to correlate with specific tickets

### Backward Compatibility Options

The ticket asks about keeping `tf ralph ... --session` accepted but not forwarded:

- CLI currently accepts `--session` flag? **NO** - The `tf ralph run/start` commands do NOT currently accept a `--session` flag from users
- The `--session` is constructed internally and passed to `pi`

So backward compatibility here likely means:
- If users were somehow relying on session files being in specific locations, this would break
- The change is internal - no user-facing flag is being removed

## Sources
- `tf_cli/ralph.py` - Main Ralph implementation
- `tests/test_ralph_session_dir.py` - Session directory tests
- `.tf/knowledge/topics/seed-remove-session-param-from-ralph/` - Seed topic
- `docs/ralph.md` - Ralph documentation
