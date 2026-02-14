# Review: pt-699h

## Critical (must fix)

- `tf/ralph.py:136-137,2485-2490` - Parallel mode is effectively disabled under default settings. `attemptTimeoutMs` defaults to `600000`, and any `base_timeout_ms > 0` forces `use_parallel = 1`. That means `tf ralph start --parallel N` silently degrades to serial unless timeout is manually set to 0, which blocks the main ticket goal (parallel dispatch scheduling).

- `tf/ralph.py:2421-2423,2859-2924` - `execution_backend` is resolved but not honored in the parallel branch. The parallel path always launches raw `subprocess.Popen(["pi", "-p", ...])` and never uses dispatch orchestration/completion APIs (`run_ticket_dispatch`/completion polling). This does not implement a real parallel *dispatch* flow and makes `--dispatch` vs `--no-interactive-shell` behavior inconsistent in parallel mode.

- `tf/ralph.py:2926-2958` - On the first non-zero exit code, the function returns immediately without terminating/waiting remaining sibling processes in the batch and without cleaning their worktrees/tracking. This can leave background `pi` processes running and leave the repository/worktree state partially unmanaged.

## Major (should fix)

- `tf/ralph.py:2880-2893,2993` - Worktree creation failure for one ticket is logged and `continue`d, but batch execution continues and `iteration` is still incremented by `len(selected)`. This can under-process tickets, distort loop accounting, and still end with `<promise>COMPLETE</promise>` despite launch failures.

- `tf/ralph.py:2919-2924` - `open(...)` + `subprocess.Popen(...)` in the launch loop are not protected by `try/finally`. If `Popen` raises (or an early exception occurs), file handles and newly created worktrees are not cleaned up, and the loop exits abruptly.

## Minor (nice to fix)

- `tf/ralph.py:133` - `parallelAutoMerge` is defined in defaults but never consumed anywhere in this file. Dead config increases confusion and suggests intended behavior is missing.

- `tf/ralph.py:2904-2906,2917-2919` - `jsonl_path` is used only as a boolean gate, but the actual output path is different (`worktree_logs/...`). This is misleading and makes reasoning about capture paths harder.

## Warnings (follow-up)

- No evidence in this change of automated coverage for:
  - parallel mode with `--dispatch`
  - partial batch launch failure
  - first-ticket failure with other tickets still running
  - cleanup behavior for remaining active processes/worktrees

## Suggestions (follow-up)

- Refactor the parallel launcher to use one explicit “active batch” structure and a `finally` cleanup phase that always:
  1) waits/terminates remaining children,
  2) closes all open handles,
  3) cleans or preserves worktrees deterministically.

- Reuse the dispatch completion utilities from `tf/ralph_completion.py` in parallel mode so dispatch semantics are consistent across serial and parallel execution.

- Add integration tests for backend parity (`dispatch` vs `subprocess`) and failure-path cleanup invariants (no orphan children, no stale worktrees, deterministic state updates).
