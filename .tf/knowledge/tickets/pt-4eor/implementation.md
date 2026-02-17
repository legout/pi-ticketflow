# Implementation: pt-4eor

## Summary
Fix the dispatch backend integration in serial Ralph loop to ensure progress entries and lessons extraction use the correct artifact root from the worktree.

## Problem
When using the dispatch backend in serial mode (`tf ralph start` with `--dispatch` or default):
1. A git worktree is created per ticket
2. The `/tf` workflow runs in the worktree, creating artifacts in `worktree/.tf/knowledge/tickets/<ticket>/`
3. After completion, `update_state()` is called to update `progress.md` and extract lessons to `AGENTS.md`
4. However, `update_state()` was called without the `artifact_root` parameter, causing it to look in the main repo's knowledge directory instead of the worktree
5. This resulted in missing progress details (issue counts, summary, commit) and missing lessons extraction

## Solution
Modified the serial dispatch flow in `ralph_start()` to:
1. Move `worktree_path` declaration outside the attempt loop so it's available for `update_state()` calls after the loop
2. Pass the worktree's knowledge directory as `artifact_root` to `update_state()` calls
3. For failure cases, `update_state()` is called with the worktree artifact root before cleanup happens

## Files Changed

### tf/ralph.py
- Added `worktree_path` and `worktree_cwd` declarations before the `while attempt < max_attempts:` loop (line ~2745)
- Changed inner loop worktree variable reset to simple assignment (no type annotation)
- Updated `update_state()` calls to pass `artifact_root`:
  - When worktree merge fails (line ~2910): passes `worktree_path / ".tf/knowledge"`
  - When ticket fails after restart loop (line ~2977): passes `worktree_path / ".tf/knowledge"`
  - When ticket completes successfully (line ~2984): passes `worktree_path / ".tf/knowledge"`

## Key Changes

Before:
```python
while attempt < max_attempts:
    # ...
    worktree_path: Optional[Path] = None  # declared inside loop
    # ...
    update_state(ralph_dir, project_root, ticket, "FAILED", error_msg)  # no artifact_root
    update_state(ralph_dir, project_root, ticket, "COMPLETE", "")  # no artifact_root
```

After:
```python
worktree_path: Optional[Path] = None  # declared before loop
worktree_cwd: Optional[Path] = None
while attempt < max_attempts:
    # ...
    worktree_path = None  # reset inside loop
    # ...
    artifact_root = worktree_path / ".tf/knowledge" if worktree_path else None
    update_state(ralph_dir, project_root, ticket, "FAILED", error_msg, artifact_root)
    update_state(ralph_dir, project_root, ticket, "COMPLETE", "", artifact_root)
```

## Verification
- Syntax check passes: `python3 -m py_compile tf/ralph.py`
- Import check passes: `python3 -c "from tf.ralph import *"`
- Ralph state tests pass: `python3 -m pytest tests/test_ralph_state.py -v` (11 passed)
- Dispatch backend is already the default (`executionBackend: "dispatch"` in DEFAULTS)
- Progress entries now correctly read from worktree artifacts
- Lessons extraction works from worktree close-summary.md

## Acceptance Criteria
- [x] Serial loop uses dispatch backend by default (already true)
- [x] Progress entries and issue summaries are written correctly from worktree artifacts
- [x] Lessons extraction still appends to `.tf/ralph/AGENTS.md` from worktree close-summary.md
