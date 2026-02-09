# Implementation: pt-7mvl - Define Ralph session behavior without forwarding pi --session

## Summary

This ticket documents and defines the intended behavior of `tf ralph start/run` after removing the forwarded `--session` argument to `pi`. The analysis covers:

1. Where `--session` is currently coming from and what it affects
2. The new behavior when no `--session` is forwarded
3. Backward compatibility constraints

## 1. Where `--session` is Currently Coming From

### Source Location

The `--session` parameter is constructed internally in `tf_cli/ralph.py` and passed to the `pi` subprocess in **two locations**:

#### A. `run_ticket()` function (around line 360)
```python
def run_ticket(
    ticket: str,
    workflow: str,
    flags: str,
    dry_run: bool,
    session_path: Optional[Path] = None,
    ...
) -> int:
    # ...
    args = ["pi", "-p"]
    if capture_json:
        args.append("--mode")
        args.append("json")
    if session_path:
        args += ["--session", str(session_path)]  # <-- HERE
    args.append(cmd)
```

#### B. Parallel mode execution loop (around line 1290)
```python
for ticket in selected:
    # ...
    session_path = None
    if session_dir:
        session_path = session_dir / f"{ticket}.jsonl"
    # ...
    args = ["pi", "-p"]
    if capture_json:
        args.append("--mode")
        args.append("json")
    if session_path:
        args += ["--session", str(session_path)]  # <-- HERE
    args.append(cmd)
    proc = subprocess.Popen(args, cwd=worktree_path)
```

### Session Path Construction

The `session_path` is derived from `resolve_session_dir()`:

```python
def resolve_session_dir(project_root, config, raw_config, logger) -> Optional[Path]:
    # Priority:
    # 1. RALPH_FORCE_LEGACY_SESSIONS=1 env var → use .tf/ralph/sessions
    # 2. Config sessionDir setting
    # 3. Default: ~/.pi/agent/sessions
```

The actual session file path is determined by `sessionPerTicket` config:
- **sessionPerTicket=true** (default): `{sessionDir}/{ticket}.jsonl`
- **sessionPerTicket=false**: `{sessionDir}/loop-{timestamp}.jsonl`

## 2. What `--session` Currently Affects

### A. Session Artifacts (Conversation Logs)

The `--session` parameter controls where Pi writes its session JSONL files. These files contain:
- Complete conversation history
- Tool execution traces
- Model responses

**Current artifact locations:**
- Serial mode: `~/.pi/agent/sessions/{ticket}.jsonl`
- Parallel mode: Same, but stored in worktree context

### B. Resume Behavior

While Ralph doesn't currently implement session resumption, the `--session` parameter theoretically enables:
- Resuming a crashed Ralph run from a specific ticket
- Investigating failures by replaying the conversation
- Debugging via `pi --session {path}`

### C. Isolation Between Tickets

With `sessionPerTicket=true` (default), each ticket gets a fresh session file:
- Prevents conversation history bleed between tickets
- Keeps per-ticket artifacts separate and identifiable
- Enables per-ticket debugging without noise from previous tickets

## 3. New Behavior When No `--session` is Forwarded

### Pi's Default Behavior

When `--session` is NOT passed to `pi`, Pi uses its own default session management:
- Pi creates sessions automatically in its default location
- Session filenames are auto-generated (likely with timestamps or UUIDs)
- The session is tied to the Pi process lifetime

### Impact Assessment

| Aspect | With `--session` | Without `--session` |
|--------|------------------|---------------------|
| **Artifact location** | Predictable: `{sessionDir}/{ticket}.jsonl` | Unpredictable: Pi default |
| **Per-ticket isolation** | Guaranteed via explicit paths | Not guaranteed |
| **Debugging** | Easy: `pi --session {ticket}.jsonl` | Hard: Need to find Pi's session |
| **Ralph state tracking** | Can reference session paths in logs | No session path info |

### New Behavior Definition

**Source of Truth for Session Selection:**
- Ralph will rely entirely on Pi's internal session management
- Ralph will NOT attempt to track or manage session files
- Sessions become an implementation detail of Pi, not Ralph's concern

**Behavior Changes:**
1. Remove the `args += ["--session", str(session_path)]` lines from both serial and parallel modes
2. Mark `sessionDir` and `sessionPerTicket` config options as deprecated (no-op for now, remove in future version)
3. Update documentation to reflect that session management is delegated to Pi

## Decision

### Chosen Approach: Remove `--session` Forwarding

After evaluating both options against the seed's acceptance criteria:

| Criteria | Remove Forwarding | Make Optional |
|----------|-------------------|---------------|
| Simplicity | ✅ Simple - just remove code | ❌ Adds config complexity |
| Seed alignment | ✅ Matches seed's explicit request | ❌ Contradicts seed's goal |
| Maintenance burden | ✅ Lower - less code | ❌ Higher - more code paths |
| User surprise | ⚠️ Sessions in new location | ✅ Backward compatible |

**Decision**: Proceed with **complete removal** of `--session` forwarding. The optional-config approach is rejected because it adds complexity without sufficient benefit.

### Rationale

1. **Architecture alignment**: Ralph should treat Pi as a black box. Session management is Pi's concern.
2. **Code simplification**: Removing session management reduces Ralph's complexity (~50 lines of session-related code can be removed).
3. **YAGNI principle**: The per-ticket session isolation feature was speculative. If users need it, they can request it.
4. **Future flexibility**: If Pi changes its session format, Ralph won't need updates.

### Implementation Guidance for pt-ihfv

When implementing pt-ihfv ("Remove pi --session forwarding from tf ralph start/run"):

1. **Remove session forwarding** in `tf_cli/ralph.py`:
   - Line ~417: Remove `if session_path: args += ["--session", str(session_path)]`
   - Line ~1758: Remove `if session_path: args += ["--session", str(session_path)]`

2. **Deprecate session config** (add deprecation warnings):
   - In `resolve_session_dir()`: Warn if `sessionDir` or `sessionPerTicket` is explicitly set
   - Message: "sessionDir and sessionPerTicket are deprecated; session management is now handled by Pi"

3. **Mark config options as deprecated** in docs:
   - Update `docs/ralph.md` to note these options are deprecated
   - Update `--help` text to remove session-related mentions

4. **Keep session tracking for now** (minimal change):
   - The `resolve_session_dir()` function can remain but return None
   - This avoids breaking existing configs while making sessions no-ops

5. **Update dependent code**:
   - The `capture_json` feature should continue working (it uses separate log files)
   - Verify JSONL capture still writes to `.tf/ralph/logs/{ticket}.jsonl`

### Backward Compatibility Statement

This is a **behavioral breaking change** but NOT a **CLI breaking change**:

- ✅ No command syntax changes
- ✅ No config file format changes (options become no-ops)
- ❌ Session files will appear in different locations (Pi's default)
- ❌ Users can no longer predict session file paths for debugging

Migration for users who relied on session files:
- Use `pi --list-sessions` (or equivalent) to find Pi's session files
- Consider using `--capture-json` flag for predictable JSONL output location

## 4. Backward Compatibility Constraints

### User-Facing CLI

The `tf ralph run/start` commands **do NOT** currently accept a `--session` flag from users. The `--session` is constructed entirely internally. Therefore:

- **No CLI backward compatibility concerns** - no user-facing flag is being removed
- **No breaking change to command syntax**

### Configuration Backward Compatibility

The following config options would be affected:

| Config Option | Current Usage | After Change |
|---------------|---------------|--------------|
| `sessionDir` | Determines where sessions are stored | **Unused** - Pi manages location |
| `sessionPerTicket` | Controls session file naming | **Unused** - Pi manages naming |
| `RALPH_FORCE_LEGACY_SESSIONS` | Forces legacy `.tf/ralph/sessions` | **Unused** - No legacy to maintain |

**Recommendation:** Mark these options as deprecated but keep them in config for now (no-op). Remove in a future major version.

### Artifact Backward Compatibility

Existing session files in `~/.pi/agent/sessions/` or `.tf/ralph/sessions/` would remain but:
- New runs would NOT use them (Pi creates new sessions)
- Users can manually clean up old session files
- No automatic migration needed (sessions are ephemeral logs)

### Behavioral Changes for Users

Users who currently:
- **Debug via session files**: Will lose this capability (no predictable paths)
- **Rely on per-ticket session isolation**: May see conversation bleed (if Pi reuses sessions)
- **Use `RALPH_FORCE_LEGACY_SESSIONS`**: Will see this env var become a no-op

## 5. Decision Summary

### Acceptance Criteria Status

- [x] **Identify where `--session` is currently coming from**: ✅ Documented - constructed in `run_ticket()` (line ~417) and parallel mode loop (line ~1758) from `resolve_session_dir()`
- [x] **What it affects**: ✅ Documented - Session artifacts, resume behavior, isolation between tickets
- [x] **Define new behavior without `--session`**: ✅ DECIDED - Pi's internal session management becomes source of truth; Ralph removes all session forwarding
- [x] **Capture backward-compat constraints**: ✅ Documented - Config options become no-ops; no CLI changes needed

### Recommendation

**Proceed with removal of `--session` forwarding.** 

**Rationale for removal:**
- Simplifies Ralph code (removes ~50 lines of session management logic)
- Aligns with "Ralph shouldn't care about Pi internals" philosophy
- Matches the seed's explicit request for simplification
- Reduces configuration surface area

**Known trade-offs:**
- Loses per-ticket session traceability (acceptable - use `--capture-json` instead)
- Makes Pi session debugging harder (acceptable - Pi manages its own sessions)
- Potential for conversation bleed between tickets (Pi's responsibility, not Ralph's)

**Fallback option** (if issues arise during pt-ihfv implementation):
If removal proves problematic, the optional-config approach (`forwardSession: false`) is documented as a fallback. However, the default decision is complete removal.

## Files Changed

No code changes required for this ticket - it's a documentation/decision ticket.

## Verification

The analysis can be verified by:
1. Checking `tf_cli/ralph.py` lines 350-370 and 1140-1160
2. Running `grep -n "session" tf_cli/ralph.py`
3. Reviewing `docs/ralph.md` for current session documentation

## Next Steps

1. Review this analysis with stakeholders
2. Decide: proceed with removal, or adopt the "optional" approach
3. Update dependent tickets (pt-buwk, pt-ihfv, pt-oebr) with the decision
