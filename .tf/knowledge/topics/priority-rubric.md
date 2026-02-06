# Priority Rubric: P0–P4 Mapping

Canonical mapping from severity labels (P0–P4) to Ticketflow numeric priorities (0–4).

## Mapping Table

| Label | Numeric | Name | Description |
|-------|---------|------|-------------|
| P0 | 0 | **Critical** | System down, data loss, security breach, blocking all work |
| P1 | 1 | **High** | Major feature, significant bug affecting users, performance degradation |
| P2 | 2 | **Normal** | Standard product features, routine enhancements (default) |
| P3 | 3 | **Low** | Engineering quality, dev workflow improvements, tech debt |
| P4 | 4 | **Minimal** | Code cosmetics, refactors, docs polish, test typing |

## P0 vs P1 Semantics

**P0 (Critical)** requires immediate attention:
- Production outage or service unavailability
- Data corruption or loss
- Security vulnerability (exploitable)
- Legal/compliance blocker
- *Action*: Drop everything, fix immediately

**P1 (High)** is important but not emergent:
- Major feature for upcoming release
- Significant user-facing bug
- Performance issues with workaround
- *Action*: Schedule within current sprint/cycle

## Ambiguous/Unknown Handling

When priority cannot be determined:

1. **Default to current priority** - Do not change if ambiguous
2. **Flag for human review** - Add note: "Priority unclear: [reason]"
3. **Use keyword heuristics** - See classification guide below
4. **Skip with explanation** - Document why classification was skipped

## Classification Keywords

### P0 Indicators (Critical: 0)
- Security: "CVE", "vulnerability", "exploit", "breach", "XSS", "injection"
- Data: "data loss", "corruption", "rollback", "recovery"
- System: "outage", "down", "crash loop", "OOM", "deadlock"
- Compliance: "GDPR", "legal", "compliance violation"

### P1 Indicators (High: 1)
- User impact: "user-facing", "customer reported", "regression"
- Features: "release blocker", "milestone", "launch"
- Performance: "slow", "timeout", "memory leak", "high CPU"
- Correctness: "wrong results", "calculation error", "data inconsistency"

### P2 Indicators (Normal: 2)
- Standard work: "feature", "implement", "add support", "enhancement"
- Integration: "API", "webhook", "export", "import"
- Default for new tickets without clear urgency indicators

### P3 Indicators (Low: 3)
- Quality: "refactor", "cleanup", "tech debt", "architecture"
- Developer experience: "DX", "dev workflow", "build time", "CI/CD"
- Observability: "metrics", "logging", "tracing", "monitoring"
- Testing: "test coverage", "integration tests", "load tests"

### P4 Indicators (Minimal: 4)
- Polish: "typo", "formatting", "lint", "style", "naming"
- Documentation: "docs", "README", "comments", "docstrings"
- Types: "type hints", "mypy", "type safety"
- Minor: "cosmetic", "whitespace", "imports cleanup"

## Example Scenarios

| Scenario | Tags/Keywords | Priority | Rationale |
|----------|---------------|----------|-----------|
| Security vulnerability in auth | `security`, `CVE`, `auth` | P0 | Exploitable risk |
| Database corruption on write | `data-loss`, `corruption` | P0 | Irreversible damage |
| Service OOM in production | `OOM`, `production`, `crash` | P0 | System unavailable |
| User login fails intermittently | `bug`, `user-facing`, `auth` | P1 | Major user impact |
| API response time >5s | `performance`, `slow` | P1 | Degraded experience |
| Wrong calculation in billing | `correctness`, `billing` | P1 | Financial impact |
| Add new export format | `feature`, `export` | P2 | Standard feature work |
| Implement webhook support | `feature`, `integration` | P2 | Product enhancement |
| Refactor legacy module | `refactor`, `tech-debt` | P3 | Engineering quality |
| Improve CI build speed | `CI/CD`, `DX` | P3 | Dev workflow |
| Fix typo in README | `docs`, `typo` | P4 | Documentation polish |
| Add type hints to tests | `typing`, `tests` | P4 | Test code quality |

## Edge Cases

### Multiple Indicators
When a ticket matches multiple priority levels:
- Use **highest** matching priority (conservative)
- Example: "Security fix with docs update" → P0 (not P4)

### Conflicting Indicators
When indicators suggest different priorities:
- Prefer severity over type (security > feature)
- Prefer user impact over internal work
- Flag for review if truly ambiguous

### Tags vs Description
- Tags take precedence (explicit intent)
- Description keywords are secondary
- When in doubt, check with ticket creator

## Implementation Notes

This rubric is designed for:
- Automated keyword-based classification
- Manual triage guidance
- Consistent backlog prioritization

For the `/tf-reclassify-priority` command:
- Default to dry-run mode
- Show matched keywords and rationale
- Require `--apply` to update tickets
