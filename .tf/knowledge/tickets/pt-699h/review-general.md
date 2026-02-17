# Review: pt-699h

## Overall Assessment
The implementation improves cleanup behavior, but two core acceptance goals are still not met in the current code path. Parallel execution is effectively disabled under default/current timeout settings, and the parallel branch does not honor the resolved dispatch backend. As written, this still behaves as conservative parallel subprocess execution rather than true parallel dispatch scheduling.

## Critical (must fix)
- `tf/ralph.py:135,2489-2494` - Parallel mode is force-disabled whenever `attemptTimeoutMs > 0` or `maxRestarts > 0`. With the default timeout (`600000ms`) and current project config (`.tf/ralph/config.json:2-3`), `--parallel N` falls back to serial, which blocks the primary goal of parallel scheduling.
- `tf/ralph.py:2425-2427,2863-2928` - `execution_backend` is resolved but ignored in the parallel branch. Parallel always launches raw `subprocess.Popen(["pi", "-p", ...])`, so `--dispatch` and `--no-interactive-shell` are not behaviorally distinct in parallel mode.

## Major (should fix)
- `tf/ralph.py:2884-2897,3014` - Worktree creation failures are marked `FAILED` but do not mark the batch as failed; iteration still increments by `len(selected)`. This can under-process tickets while still allowing a successful overall return code.
- `tf/ralph.py:2919-2928,2930-3012` - Launching processes is not exception-safe for batch resources. If `open()`/`Popen()` raises mid-batch, previously launched child processes and worktrees are not guaranteed cleanup in this control path.

## Minor (nice to fix)
- `tf/ralph.py:2908-2910,2921-2924` - `jsonl_path` is used as a boolean gate, but the actual output file is written to a different path (`worktree_path/.tf/ralph/logs/...`). This is confusing and increases maintenance cost.

## Warnings (follow-up ticket)
- `tests/test_json_capture.py:65-69`, `tests/test_ralph_logging.py:309-370` - Current tests cover argument parsing/log formatting but there is no behavioral integration coverage for parallel-dispatch backend parity, partial launch failure handling, and cleanup invariants.

## Suggestions (follow-up ticket)
- `tf/ralph.py:2863-3015` - Refactor parallel execution into a single “active batch” structure with `try/finally` cleanup that always closes handles, waits/terminates children, and deterministically cleans or preserves worktrees.
- `tf/ralph.py:2863-2928` + `tf/ralph_completion.py` - Reuse `run_ticket_dispatch` + completion polling utilities in parallel mode so dispatch semantics match serial behavior and backend flags are honored consistently.

## Positive Notes
- `tf/ralph.py:2930-3012` now processes the whole batch and records `first_error_rc` before returning, which is safer than fail-fast mid-cleanup.
- `tf/ralph.py:825-904` now closes dispatch output file handles in a `finally` block, fixing a real resource-leak path.

## Summary Statistics
- Critical: 2
- Major: 2
- Minor: 1
- Warnings: 1
- Suggestions: 2
