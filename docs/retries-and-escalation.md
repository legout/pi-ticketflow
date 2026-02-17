# Retries and Escalation

Quality-gate blocked tickets can be automatically retried with escalated models to break out of failure loops. This document explains how retries work, how to configure them, and how Ralph handles blocked tickets.

---

## Overview

When a ticket fails to close due to quality gate violations (Critical/Major issues), the retry system can:

1. **Detect the block** from `close-summary.md` or `review.md`
2. **Increment a retry counter** persisted across Ralph iterations
3. **Escalate to stronger models** on subsequent attempts
4. **Skip exhausted tickets** after max retries exceeded

---

## How Retries Work

### Detection

When `/tf` closes a ticket, it checks for quality gate blocks:

1. **Primary**: Parse `close-summary.md` for explicit `BLOCKED` status
2. **Fallback**: Check `review.md` for nonzero counts in `workflow.failOn` severities

```markdown
<!-- close-summary.md -->
## Status
**BLOCKED**

## Summary Statistics
- Critical: 2
- Major: 1
```

### Retry State Persistence

Retry state is stored in the ticket's artifact directory:

```
.tf/knowledge/tickets/{ticket-id}/
├── retry-state.json      # Retry counter and attempt history
├── close-summary.md      # Close status and statistics
└── review.md             # Consolidated review
```

**Key properties**:
- Survives Ralph restarts (filesystem storage)
- Co-located with ticket artifacts for easy cleanup
- Atomic writes prevent corruption
- Schema versioned for future migrations

### Retry Counter Behavior

| Event | Retry Count | Status |
|-------|-------------|--------|
| Initial attempt | 0 | active |
| Blocked close | +1 | active |
| Successful close | 0 | closed |
| `--retry-reset` | 0 | active |

The counter **only resets on successful close**. Failed attempts accumulate until the ticket passes the quality gate.

---

## Configuration

Add escalation configuration to `.tf/config/settings.json`:

```json
{
  "workflow": {
    "escalation": {
      "enabled": false,
      "maxRetries": 3,
      "models": {
        "fixer": null,
        "reviewerSecondOpinion": null,
        "worker": null
      }
    }
  }
}
```

> `.tf/config/settings.json` is derived from `config/settings.json` via `/tf-sync`. Keeping the escalation block in both files ensures the new defaults are versioned in the repository while the project override stays up to date.

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable retry/escalation behavior |
| `maxRetries` | integer | `3` | Maximum BLOCKED attempts before skipping |
| `models.fixer` | string \| null | `null` | Escalation model for fixer role |
| `models.reviewerSecondOpinion` | string \| null | `null` | Escalation model for 2nd opinion reviewer |
| `models.worker` | string \| null | `null` | Escalation model for implementation |

**Note**: `null` means "use base model from `agents` config" (no escalation).

### Role Mapping

Each escalation override corresponds to a workflow role so you can target the exact phase that needs a stronger model:

- `workflow.escalation.models.fixer` → fixer agent (`agents.fixer`). Applied during the Fix Issues step on retry attempts.
- `workflow.escalation.models.reviewerSecondOpinion` → second-opinion reviewer agent (`reviewer-second-opinion`). Used when merging reviews on attempt 3+.
- `workflow.escalation.models.worker` → worker agent (`agents.worker`). Applies to implementation attempts that hit the third retry and beyond.

Set any override to `null` to fall back to the base model derived from `agents` → `metaModels`. When `enabled` remains `false`, the workflow continues to use base models for every role, so the change is backwards compatible.

### Escalation Curve

Models are escalated based on attempt number:

| Attempt | Fixer | Reviewer-2nd-Opinion | Worker |
|---------|-------|---------------------|--------|
| 1 | Base model | Base model | Base model |
| 2 | Escalation model | Base model | Base model |
| 3+ | Escalation model | Escalation model | Escalation model (if configured) |

**Example escalation config**:

```json
{
  "workflow": {
    "escalation": {
      "enabled": true,
      "maxRetries": 3,
      "models": {
        "fixer": "zai/glm-4.7",
        "reviewerSecondOpinion": "openai-codex/gpt-5.2-codex",
        "worker": null
      }
    }
  }
}
```

---

## Ralph Integration

### Automatic Retry Detection

Ralph checks `retry-state.json` before selecting tickets:

1. Load retry state (if exists)
2. If `status: blocked` and `retryCount >= maxRetries`:
   - Skip ticket in `tk ready` results
   - Log: `Skipping pt-123: max retries (3) exceeded`
3. Otherwise, include ticket with escalation context

### Progress Tracking

Ralph logs retry context to `.tf/ralph/progress.md`:

```markdown
- pt-123: COMPLETE (2026-02-10T14:30:00Z)
  - Summary: Fix authentication bug
  - Issues: Critical(0)/Major(0)/Minor(1)
  - Retry: Attempt 2, Count 1
  - Status: COMPLETE
```

### Parallel Worker Safety

**Important**: Retry logic assumes `ralph.parallelWorkers: 1` (default).

When `parallelWorkers > 1`:
- Multiple workers may race on the same `retry-state.json`
- Recommend either:
  - **Option A**: Disable retry logic (`escalation.enabled: false`)
  - **Option B**: Implement file locking (requires additional setup)

---

## Manual Override

### Force Reset

To discard retry history and start fresh:

```bash
/tf pt-123 --retry-reset
```

**Behavior**:
1. Renames `retry-state.json` → `retry-state.json.bak.{timestamp}`
2. Starts with attempt #1
3. Uses base models (no escalation)

Use `--retry-reset` when:
- You've manually fixed the underlying issues
- The ticket context has significantly changed
- Retry state appears corrupted

### Check Retry State

View current retry state:

```bash
cat .tf/knowledge/tickets/pt-123/retry-state.json
```

Example output:

```json
{
  "version": 1,
  "ticketId": "pt-123",
  "attempts": [
    {
      "attemptNumber": 1,
      "startedAt": "2026-02-10T12:00:00Z",
      "completedAt": "2026-02-10T12:30:00Z",
      "status": "blocked",
      "trigger": "initial",
      "qualityGate": {
        "failOn": ["Critical", "Major"],
        "counts": {
          "Critical": 2,
          "Major": 1,
          "Minor": 0,
          "Warnings": 0,
          "Suggestions": 0
        }
      },
      "escalation": {
        "fixer": null,
        "reviewerSecondOpinion": null,
        "worker": null
      }
    }
  ],
  "lastAttemptAt": "2026-02-10T12:00:00Z",
  "status": "active",
  "retryCount": 1
}
```

---

## Retry State Schema

### File Location

```
.tf/knowledge/tickets/{ticket-id}/retry-state.json
```

### Schema Structure

```typescript
{
  version: 1,                    // Schema version
  ticketId: string,              // Ticket identifier
  attempts: [{
    attemptNumber: number,       // 1-indexed attempt number
    startedAt: string,           // ISO 8601 timestamp
    completedAt?: string,        // ISO 8601 timestamp
    status: "in_progress" | "blocked" | "closed" | "error",
    trigger: "initial" | "quality_gate" | "manual_retry" | "ralph_retry",
    qualityGate?: {
      failOn: string[],
      counts: {
        Critical: number,
        Major: number,
        Minor: number,
        Warnings: number,
        Suggestions: number
      }
    },
    escalation?: {
      fixer?: string | null,
      reviewerSecondOpinion?: string | null,
      worker?: string | null
    }
  }],
  lastAttemptAt: string,         // Timestamp of most recent attempt
  status: "active" | "blocked" | "closed",
  retryCount: number             // Number of blocked attempts
}
```

---

## Best Practices

### 1. Start with Defaults

Leave `enabled: false` until you understand your failure patterns:

```json
{
  "workflow": {
    "escalation": {
      "enabled": false
    }
  }
}
```

### 2. Enable Conservatively

When enabling escalation, start with just the fixer:

```json
{
  "models": {
    "fixer": "stronger-model",
    "reviewerSecondOpinion": null,
    "worker": null
  }
}
```

### 3. Monitor Retry Patterns

Check `.tf/ralph/progress.md` for retry trends:

```bash
grep -E "Retry: Attempt|Skipping" .tf/ralph/progress.md
```

Frequent retries may indicate:
- Quality gate is too strict
- Tickets are under-specified
- Escalation models aren't helping

### 4. Clean Up Old State

When deleting tickets, retry state is automatically removed:

```bash
tk rm pt-123  # Removes .tf/knowledge/tickets/pt-123/ including retry-state.json
```

---

## Troubleshooting

### Ticket keeps getting retried indefinitely

**Check**:
1. Is `maxRetries` configured correctly?
2. Is `escalation.enabled` set to `true`?
3. Is post-fix re-review enabled? (Required for quality gate to work)

### Escalation not applying

**Check**:
1. Is `attemptNumber >= 2` in retry-state.json?
2. Are escalation models configured (not `null`)?
3. Is Ralph using the correct settings.json?

### Retry state corruption

**Fix**:
```bash
/tf pt-123 --retry-reset
```

---

## Related Documentation

- [Ralph Loop](./ralph.md) - Autonomous ticket processing
- [Configuration](./configuration.md) - Full settings.json reference
- [Workflows](./workflows.md) - TF workflow details
- [Quality Gates](./guardrails.md) - Review and gate configuration
