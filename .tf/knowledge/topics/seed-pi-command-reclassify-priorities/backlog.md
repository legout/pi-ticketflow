# Backlog: seed-pi-command-reclassify-priorities

| ID | Title | Est. Hours | Score | Depends On | Component Tags | Links |
|----|-------|------------|-------|------------|----------------|-------|
| pt-zoqp | Define priority rubric mapping (P0–P4 → tk priority 0–4) | 1-2 | 6 | - | component:cli, component:docs, component:workflow | - |
| pt-gn5z | Design + setup /tf-priority-reclassify prompt and Python entrypoint | 1-2 | 15 | pt-zoqp | component:agents, component:cli, component:config, component:docs, component:workflow | pt-ctov |
| pt-qqwc | Implement ticket selection for priority reclassify (ids/ready/status/tag) | 1-2 | 3 | pt-gn5z | component:cli, component:workflow | pt-1fsy |
| pt-1fsy | Implement rubric-based priority classifier + rationale generation | 1-2 | 3 | pt-qqwc | component:cli, component:docs, component:tests, component:workflow | pt-qqwc |
| pt-psvv | Implement dry-run output + optional reclassify report artifact | 1-2 | 3 | pt-1fsy | component:api, component:cli, component:config, component:docs, component:workflow | pt-xue1 |
| pt-xue1 | Implement --apply: update ticket frontmatter priority safely (+ audit note) | 1-2 | 3 | pt-psvv | component:cli, component:docs, component:workflow | pt-psvv, pt-zwns |
| pt-6ztc | Add safety UX: confirmation, change limits, and skip/force controls | 1-2 | 0 | pt-xue1 | component:cli, component:workflow | - |
| pt-zwns | Test priority reclassify: classifier rules + apply mode (tmp tickets) | 1-2 | 1 | pt-6ztc | component:cli, component:tests, component:workflow | pt-xue1 |
| pt-ctov | Document /tf-priority-reclassify and the P0–P4 rubric (README/docs) | 1-2 | 0 | pt-zwns | component:agents, component:cli, component:docs, component:workflow | pt-gn5z |

## Notes
- No existing backlog.md or matching open tickets were found for this seed, so nothing was skipped as a duplicate.
- Dependencies were inferred (seed mode) as a simple chain in logical implementation order.
- Links were added conservatively between tightly-related tickets.
- Active planning session detected (seed-test-session@2026-02-06T12-57-17Z, root: seed-test-session). Not finalizing it because requested topic is seed-pi-command-reclassify-priorities.
