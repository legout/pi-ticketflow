# Implementation: pt-gn5z

## Summary
Created the `/tf-priority-reclassify` Pi prompt and Python CLI entrypoint for reclassifying ticket priorities using a P0-P4 rubric.

## Files Changed
- `prompts/tf-priority-reclassify.md` - New Pi prompt file with usage, rubric, and execution instructions
- `tf_cli/priority_reclassify_new.py` - Python entrypoint implementing the reclassification logic
- `tf_cli/cli.py` - Added command handler and help text
- `tf_cli/new_cli.py` - Added command to the `new` namespace

## Key Decisions
1. **Dry-run by default**: The `--apply` flag is required to make actual changes, ensuring safety
2. **Multiple selection modes**: Supports `--ids`, `--ready`, `--status`, and `--tag` filters
3. **P0-P4 rubric implementation**:
   - P0: Critical bugs (security, crashes, data loss)
   - P1: Urgent fixes (blockers, regressions)
   - P2: Product features
   - P3: Engineering quality / workflow
   - P4: Code cosmetics / docs / cleanup
4. **Audit trail**: Writes results to `.tf/knowledge/priority-reclassify-{timestamp}.md`
5. **Closed ticket exclusion**: Automatically skips closed tickets

## Tests Run
```bash
# Syntax check
python -m py_compile tf_cli/priority_reclassify_new.py tf_cli/cli.py tf_cli/new_cli.py

# Help output verification
python -m tf_cli.priority_reclassify_new --help
python -m tf_cli --help
python -m tf_cli new priority-reclassify --help
```

All tests passed successfully.

## Verification
- [x] Prompt file created with frontmatter and usage instructions
- [x] Python entrypoint accepts `--apply`, `--ids`, `--ready`, `--status`, `--tag` flags
- [x] `--help` prints correctly via both `tf` and `tf new` namespaces
- [x] Command appears in help output for both CLI entry points
