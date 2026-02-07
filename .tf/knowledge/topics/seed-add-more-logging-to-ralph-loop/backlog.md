# Backlog: seed-add-more-logging-to-ralph-loop

| ID | Title | Est. Hours | Score | Depends On | Component Tags | Links |
|----|-------|------------|-------|------------|----------------|-------|
| pt-l6yb | Define Ralph logging spec (events, fields, redaction) | 1-2 | 6 | - | component:api, component:workflow | pt-j2it |
| pt-7cri | Configure Ralph verbosity controls (CLI flags + env var) | 1-2 | 8 | pt-l6yb | component:cli, component:config, component:docs, component:workflow | - |
| pt-rvpi | Implement Ralph logger helper (timestamped levels, stderr, redaction) | 1-2 | 3 | pt-7cri | component:api, component:workflow | pt-ljos, pt-uo6h |
| pt-ljos | Implement lifecycle logging for serial Ralph loop (start/run) | 1-2 | 3 | pt-rvpi | component:cli, component:config, component:workflow | pt-rvpi, pt-2sea |
| pt-2sea | Implement lifecycle logging for parallel Ralph mode (worktrees + batches) | 1-2 | 3 | pt-ljos | component:workflow | pt-ljos |
| pt-uo6h | Implement optional Pi JSON mode capture for deeper debugging (experimental) | 1-2 | 3 | pt-rvpi | component:api, component:cli, component:config, component:workflow | pt-rvpi |
| pt-m5jv | Test Ralph logging (serial + parallel selection) with captured stderr | 1-2 | 1 | pt-2sea | component:tests, component:workflow | - |
| pt-j2it | Document Ralph logging + troubleshooting (tf ralph start/run) | 1-2 | 0 | pt-m5jv | component:api, component:config, component:docs, component:workflow | pt-l6yb |

## Notes
- No existing backlog.md or matching tickets were found for this seed, so nothing was skipped as a duplicate.
- Dependencies were inferred (seed mode) as a simple chain reflecting the intended implementation order.
- Links were added conservatively between tightly-related tickets.
- Active planning session detected (seed-test-session@2026-02-06T12-57-17Z, root: seed-test-session). Not finalizing it because requested topic is seed-add-more-logging-to-ralph-loop.
