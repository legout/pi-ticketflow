# Review: pt-rvpi

## Overall Assessment
The structured logging implementation is well-designed with good separation of concerns, comprehensive tests, and proper context propagation for parallel execution. However, there's a critical enum mismatch between the logger module and ralph_new.py that will cause runtime crashes when certain CLI flags or config options are used.

## Critical (must fix)
- `tf_cli/ralph_new.py:306-317` - **Enum mismatch causing runtime crashes**: The code references `LogLevel.VERBOSE`, `LogLevel.QUIET`, and `LogLevel.NORMAL` which don't exist in the `LogLevel` enum (defined in `tf_cli/logger.py:15-18` as only DEBUG, INFO, WARN, ERROR). This will cause `AttributeError` at runtime when:
  - User passes `--verbose` or `--quiet` flags
  - Config file has `logLevel: "normal"` or `logLevel: "quiet"`
  - Environment variables `RALPH_VERBOSE=1`, `RALPH_DEBUG=1`, or `RALPH_QUIET=1` are set
  - Default resolution falls through to `LogLevel.NORMAL` at line 317

- `tf_cli/ralph_new.py:323-326` - **log_level_to_flag() references non-existent enum values**: The mapping dictionary uses `LogLevel.QUIET`, `LogLevel.NORMAL`, `LogLevel.VERBOSE` which don't exist, causing crashes when trying to convert log levels to workflow flags.

## Major (should fix)
- `tf_cli/logger.py:68-72` - **Regex compilation without word boundaries**: The sensitive key patterns use `|` without word boundaries, causing "myapitoken" to match both "api" and "token" patterns. This could cause false positives in legitimate key names.

- `tf_cli/logger.py:119-129` - **High entropy heuristic may have false positives**: The `_looks_like_secret()` method flags any string >30 chars with <2 spaces and >85% alphanumeric as a secret. This could redact legitimate data like UUIDs, hashes, or base64-encoded non-sensitive data.

- `tf_cli/ralph_new.py:116-125` - **Race condition in lock file handling**: The `lock_acquire()` function has a TOCTOU (time-of-check-time-of-use) race condition. Between checking if the lock exists and creating it, another process could create the lock. Consider using `fcntl` or atomic file operations.

- `tf_cli/ralph_new.py:840-844` - **Sequential wait defeats parallel purpose**: In parallel mode, `proc.wait()` is called sequentially in a loop, so if one ticket takes longer, others that finished earlier won't be cleaned up until all preceding tickets complete. Consider using `asyncio` or a completion callback pattern.

## Minor (nice to fix)
- `tf_cli/logger.py:163-165` - **Level comparison depends on enum definition order**: The `_should_log()` method compares levels by their index in a hardcoded list. If someone reorders the enum definition, filtering logic breaks. Consider using numeric severity values (DEBUG=10, INFO=20, etc.) instead.

- `tf_cli/ralph_new.py:169-173` - **No validation of ticket query**: The `sanitize_ticket_query()` fallback uses `tk ready | head -1 | awk '{print $1}'` which assumes specific output format. If `tk` changes its output format, this will break silently.

- `tf_cli/ralph_new.py:431` - **Issue counting logic treats non-FAILED as completed**: The `update_state()` function increments `completed` for any status other than "FAILED", so "SKIPPED", "CANCELLED", or custom statuses would be incorrectly counted as completed.

- `tf_cli/ralph_new.py:824` - **Worktree removal only on success**: Failed worktree adds don't get cleaned up, potentially leaving git in an inconsistent state with orphaned worktree entries.

- `tests/test_logger.py:87-88` - **Truncation test is vague**: The assertion only checks that result contains "[TRUNCATED]" and is under 60 chars, but doesn't verify exact truncation behavior or that content before the marker is correct.

## Warnings (follow-up ticket)
- `tf_cli/ralph_new.py:414-470` - **Non-atomic progress file updates**: The `update_state()` function reads, modifies, and writes the progress file without file locking. Parallel Ralph instances could corrupt the progress file. Consider using file locking (`fcntl.flock`) or atomic writes (write to temp file + rename).

- `tf_cli/logger.py:140` - **Redaction helper shared by reference**: When `with_context()` creates a new logger, it shares the same `RedactionHelper` instance. Mutating one logger's redaction settings would affect all loggers sharing that helper. Consider deep copying or making RedactionHelper immutable.

- `tf_cli/ralph_new.py:788-802` - **Component tag extraction uses manual parsing**: Instead of using a YAML parser, it manually parses frontmatter with string operations. This is fragile and could break if frontmatter format changes (e.g., quoted strings, different indentation).

## Suggestions (follow-up ticket)
- `tf_cli/logger.py:36-38` - Consider adding numeric severity values to LogLevel enum for clearer comparison logic (DEBUG=10, INFO=20, WARN=30, ERROR=40) instead of relying on list index ordering.

- `tf_cli/ralph_new.py:271` - Consider adding `--log-level` flag that accepts explicit values (debug/info/warn/error) in addition to the boolean-style flags for more flexibility.

- `tf_cli/logger.py:119-129` - Consider making the entropy threshold configurable via the RedactionHelper constructor to allow tuning for different environments.

## Positive Notes
- Excellent test coverage with 41 comprehensive tests for the logger module
- Clean separation of concerns between `RalphLogger`, `RedactionHelper`, and factory function
- Proper immutability pattern with `with_context()` creating new logger instances
- Good documentation in implementation.md with clear decisions explained
- Context propagation handles parallel mode correctly with ticket/iteration/mode fields
- Redaction is applied before string formatting, preventing secrets from ever entering formatted output
- Default stderr output is correct for logging (keeps stdout clean for actual output)
- ISO timestamp format with UTC is a good choice for consistency

## Summary Statistics
- Critical: 2
- Major: 4
- Minor: 5
- Warnings: 3
- Suggestions: 3
