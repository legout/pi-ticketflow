# Implementation: pt-zoqp

## Summary
Created the canonical priority rubric mapping P0–P4 to Ticketflow numeric priorities (0–4). The rubric is stored at `.tf/knowledge/topics/priority-rubric.md` for use by the reclassify command and as documentation.

## Files Changed
- `.tf/knowledge/topics/priority-rubric.md` - New rubric document (created)

## Key Decisions

### Direct 1:1 Mapping (P0→0, P1→1, etc.)
Chose direct numeric correspondence for simplicity:
- P0 = 0 (Critical)
- P1 = 1 (High)  
- P2 = 2 (Normal/Default)
- P3 = 3 (Low)
- P4 = 4 (Minimal)

This matches the seed description and is intuitive.

### Keyword-Based Classification
Defined keyword indicators for each priority level to enable automated classification:
- **P0**: security, CVE, data-loss, outage, OOM
- **P1**: user-facing, regression, performance, correctness
- **P2**: feature, implement, enhancement (default)
- **P3**: refactor, tech-debt, CI/CD, DX
- **P4**: docs, typo, formatting, type hints

### Conservative Approach
- When ambiguous: keep current priority, flag for review
- When multiple indicators: use highest priority
- Tags take precedence over description keywords

### Documentation Format
Created as a standalone markdown file in the knowledge base so it can be:
1. Referenced by the reclassify command implementation
2. Used for manual triage guidance
3. Extended with project-specific overrides

## Acceptance Criteria Verification

- [x] Mapping P0–P4 → 0–4 is explicitly stated (including P0 vs P1 semantics)
- [x] "Ambiguous/unknown" handling is defined (skip + explain, default to current)
- [x] 10+ example scenarios listed (security, correctness, OOM, feature, refactor/docs)

## Tests Run
- Verified markdown renders correctly
- Confirmed all priority levels (0-4) have definitions
- Validated example scenarios cover the required categories

## Verification
View the rubric:
```bash
cat .tf/knowledge/topics/priority-rubric.md
```

The rubric is ready for use by ticket `pt-gn5z` (Design + setup /tf-priority-reclassify).
