# Runtime Artifact Policy

This document defines what is **source-controlled** (committed to git) vs **runtime/generated** (local-only, gitignored) in the pi-ticketflow project.

---

## Quick Reference

| Category | Path Pattern | Status |
|----------|--------------|--------|
| Topic knowledge (plans, seeds, spikes) | `.tf/knowledge/topics/*/` | **Source-controlled** |
| Ticket artifacts (reviews, fixes) | `.tf/knowledge/tickets/*/` | **Runtime** (gitignored) |
| Ralph session logs | `.tf/ralph/sessions/` | **Runtime** (gitignored) |
| Ralph progress/lessons | `.tf/ralph/*.md` | **Source-controlled** |
| Ticket definitions | `.tickets/` | **Source-controlled** |
| Coverage reports | `htmlcov/`, `.coverage` | **Runtime** (gitignored) |
| Python build artifacts | `*.egg-info/`, `build/`, `dist/` | **Runtime** (gitignored) |
| Virtual environment | `.venv/` | **Runtime** (gitignored) |
| Cache directories | `.pytest_cache/`, `node_modules/` | **Runtime** (gitignored) |

---

## Detailed Rules

### 1. `.tf/knowledge/` — Mixed Content

The knowledge base contains both durable planning artifacts and ephemeral ticket artifacts.

#### Source-Controlled (Keep Committed)

```
.tf/knowledge/
├── index.json                    # Registry of all topics
├── topics/                       # All topic directories
│   └── {topic-id}/
│       ├── overview.md           # Summary + keywords
│       ├── sources.md            # References and URLs
│       ├── seed.md               # Greenfield ideas
│       ├── baseline.md           # Brownfield analysis
│       ├── plan.md               # Implementation plans
│       ├── spike.md              # Research findings
│       ├── backlog.md            # Generated tickets
│       ├── mvp-scope.md          # What's in/out
│       ├── risk-map.md           # Technical risks
│       ├── test-inventory.md     # Test coverage
│       └── dependency-map.md     # External dependencies
└── priority-rubric.md            # Priority classification rules
```

**Rationale**: These represent project knowledge, decisions, and plans that should persist and be shared.

#### Runtime/Local-Only (Gitignored)

```
.tf/knowledge/
└── tickets/
    └── {ticket-id}/
        ├── research.md           # Per-ticket research
        ├── implementation.md     # Implementation summary
        ├── review.md             # Consolidated review
        ├── review-general.md     # Individual reviewer output
        ├── review-spec.md        # Individual reviewer output
        ├── review-second.md      # Individual reviewer output
        ├── fixes.md              # Fixes applied
        ├── followups.md          # Follow-up tickets
        ├── close-summary.md      # Final summary
        ├── chain-summary.md      # Artifact index
        ├── files_changed.txt     # Tracked changed files
        └── ticket_id.txt         # Ticket ID
```

**Rationale**: These are ephemeral artifacts generated during the `/tf` workflow. They can be regenerated and don't need to persist in git.

---

### 2. `.tf/ralph/` — Mixed Content

#### Source-Controlled (Keep Committed)

```
.tf/ralph/
├── AGENTS.md                     # Lessons learned (if exists)
└── progress.md                   # Progress tracking
```

**Rationale**: Lessons learned and progress tracking provide value across sessions.

#### Runtime/Local-Only (Gitignored)

```
.tf/ralph/
└── sessions/                     # Session logs and subagent artifacts
    ├── *.jsonl                   # Session transcripts
    ├── run-*/                    # Run-specific logs
    └── subagent-artifacts/       # Subagent output files
```

**Rationale**: Session logs are large, ephemeral, and can be regenerated. They may contain sensitive context.

---

### 3. `.tickets/` — Source-Controlled

All files in `.tickets/` are source-controlled. These are the ticket definitions managed by the `tk` CLI.

**Rationale**: Tickets represent work items that should be tracked and shared.

---

### 4. Build/Runtime Artifacts — Gitignored

The following patterns are runtime-generated and should never be committed:

```
# Python
*.egg-info/
build/
dist/
__pycache__/
*.pyc
.venv/

# Testing
.coverage
htmlcov/
.pytest_cache/

# Node
node_modules/

# TF Workflow
.tf/knowledge/tickets/
.tf/ralph/sessions/
```

---

## Contributor Guidelines

### When Adding New Directories

1. **Ask**: Is this generated during workflow execution?
   - Yes → Add to `.gitignore`
   - No → Keep source-controlled

2. **Ask**: Can it be regenerated from other files?
   - Yes → Consider gitignoring
   - No → Keep source-controlled

3. **Ask**: Does it contain sensitive/local-only data?
   - Yes → Gitignore it
   - No → Evaluate other criteria

### Before Committing

Run a quick check:

```bash
# See what would be added
git status

# Check for large/generated files
du -sh .tf/knowledge/tickets/ 2>/dev/null || echo "No ticket artifacts"
du -sh .tf/ralph/sessions/ 2>/dev/null || echo "No session logs"

# Ensure .gitignore is working
git check-ignore -v path/to/file
```

### Common Mistakes to Avoid

- ❌ Committing `.tf/knowledge/tickets/*/review*.md` files
- ❌ Committing session logs from `.tf/ralph/sessions/`
- ❌ Committing `*.egg-info/` directories
- ❌ Committing `htmlcov/` coverage reports
- ✅ Committing topic plans in `.tf/knowledge/topics/`
- ✅ Committing ticket definitions in `.tickets/`

---

## Maintenance

This policy should be reviewed when:

1. New workflow phases add new artifact types
2. New directories are added to the project
3. Contributors report confusion about what to commit

To update this policy:

1. Edit `docs/artifact-policy.md`
2. Update `.gitignore` if needed
3. Announce changes in commit message

---

## Related Documentation

- [Architecture](architecture.md) — Overall system design
- [Configuration](configuration.md) — Project configuration
- [Workflows](workflows.md) — How artifacts are generated
