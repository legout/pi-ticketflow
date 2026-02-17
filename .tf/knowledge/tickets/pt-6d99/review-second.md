# Review: pt-6d99

## Overall Assessment
The execution backend contract is well-structured with proper flag parsing and config precedence. However, several edge cases in the resolution logic, incomplete error handling for invalid config values, and potential confusion between the `interactiveShell.enabled` fallback and explicit `executionBackend` setting could lead to unexpected behavior. The deferred implementation (using subprocess for both backends) is appropriately marked with TODOs but may confuse users.

## Critical (must fix)
- `tf/ralph.py:1510` - No validation that `execution_backend` value is actually "dispatch" or "subprocess". Invalid config values silently fall through to default. The code checks `config_backend in ("dispatch", "subprocess")` but if it fails, it falls back silently without logging.

## Major (should fix)
- `tf/ralph.py:1467` and `tf/ralph.py:1703` - Both `ralph_run()` and `ralph_start()` have duplicate, nearly identical execution backend resolution logic. This is a maintenance risk; consider extracting to a shared `resolve_execution_backend()` function.
- `tf/ralph.py:1506-1514` - The fallback logic checking `interactiveShell.enabled` is subtle and may cause confusion: if `executionBackend` is invalid/missing but `interactiveShell.enabled: false` exists, it switches to subprocess silently. Users may not understand why their config isn't being respected.
- `tf/ralph.py:676-678` - The log message says "Execution backend: dispatch (interactive_shell) - NOTE: using subprocess fallback until pt-9yjn". This is misleading because it claims dispatch mode but then admits it's using subprocess. Users may believe dispatch is working when it's not.

## Minor (nice to fix)
- `tf/ralph.py:68-73` - `interactiveShell.mode` config option is defined but never used. The code only checks `interactiveShell.enabled`. Either remove this unused option or document that it's reserved for future use.
- `tf/ralph.py:1508` - The type check `isinstance(config_backend, str)` is defensive but inconsistent with other config resolution functions that don't validate types (e.g., `resolve_attempt_timeout_ms`). Consider consistent validation strategy.
- `tf/ralph.py:140` - Help text says "CLI flags take precedence over environment variables" but the actual code in `ralph_run()` and `ralph_start()` checks env vars before config, not CLI flags before env vars in a single function. The precedence is correct but the code structure makes it harder to verify.

## Warnings (follow-up ticket)
- `tf/ralph.py:676` - The TODO for pt-9yjn should include a tracking issue or at least a date. Without actual dispatch implementation, this contract is "dead code" from user perspective - flags are parsed but behavior is identical.
- `tf/ralph.py:1467-1514` and `tf/ralph.py:1703-1749` - When pt-9yjn implements actual dispatch, the two code paths will diverge significantly. The current structure doesn't make it easy to see where the actual backend switch will happen.

## Suggestions (follow-up ticket)
- Add a `tf ralph config` subcommand or `--show-config` flag to help users debug why a particular backend was selected. The precedence chain (CLI → env → config → default) is complex enough that users will need debugging tools.
- Consider adding a warning log when falling back from invalid `executionBackend` config value to default, so users know their config has a typo.
- The `--dispatch` flag is redundant since it's the default. Consider deprecating it or making it a no-op that just confirms intent, but document clearly.

## Positive Notes
- Clean separation between CLI flag parsing and backend resolution logic
- Good backward compatibility handling with `interactiveShell.enabled` fallback
- Environment variable `RALPH_NO_INTERACTIVE_SHELL` follows existing naming conventions
- Clear documentation in `usage()` explaining the flag semantics
- Both `ralph run` and `ralph start` support the new flags consistently

## Summary Statistics
- Critical: 1
- Major: 3
- Minor: 3
- Warnings: 2
- Suggestions: 3
