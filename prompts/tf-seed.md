---
description: Capture greenfield idea into seed artifacts with automatic session activation [tf-planning +codex-mini]
model: openai-codex/gpt-5.3-codex
thinking: medium
skill: tf-planning
---

# /tf-seed

Capture an initial idea into structured seed artifacts and activate a planning session.

## Usage

```
/tf-seed <idea description>
/tf-seed --no-session <idea description>
/tf-seed --active
/tf-seed --sessions [seed-id]
/tf-seed --resume <seed-id|session-id>
```

## Arguments

- `$@` - The idea to capture (can be multiple words)

## Flags

| Flag | Description |
|------|-------------|
| `--no-session` | Create seed artifacts without activating a planning session |
| `--active` | Print the current active session (or "none") |
| `--sessions [seed-id]` | List archived sessions, optionally filtered by seed |
| `--resume <id>` | Resume an archived session by seed-id or session-id |

## Examples

```bash
# Create seed and activate a new planning session (default)
/tf-seed Build a CLI tool for managing database migrations

# Create seed without session activation (legacy behavior)
/tf-seed --no-session Build a CLI tool

# Show current active session
/tf-seed --active

# List all archived sessions
/tf-seed --sessions

# List sessions for a specific seed
/tf-seed --sessions seed-my-idea

# Resume latest session for a seed
/tf-seed --resume seed-my-idea

# Resume specific session by ID
/tf-seed --resume seed-my-idea@2026-02-06T12-30-00Z
```

## Execution

Follow the **TF Planning Skill** "Seed Capture" procedure:

1. Parse idea and flags from `$@`
2. Handle query flags (`--active`, `--sessions`, `--resume`) if present
3. Create topic ID: `seed-{slug}`
4. Create directory: `.tf/knowledge/topics/{id}/`
5. Write seed artifacts (overview.md, seed.md, etc.)
6. Update `index.json`
7. **Activate planning session** (unless `--no-session`):
   - If an active session exists, archive it first
   - Create and activate new session for this seed
   - Emit: `[tf] Activated planning session: {session_id} (root: {seed-id})`

## Session Behavior

### Default Behavior (Session Activation)

By default, `/tf-seed` creates a **planning session** that links subsequent `/tf-spike`, `/tf-plan`, and `/tf-backlog` operations to this seed:

- Creates `.active-planning.json` with session metadata
- Session ID format: `{seed-id}@{YYYY-MM-DDTHH-MM-SSZ}`
- Archives any existing active session before switching

### Legacy Behavior (`--no-session`)

Use `--no-session` to create seed artifacts without session activation:

- No `.active-planning.json` is created or modified
- No archiving of existing sessions
- Use this for standalone seeds that won't use the session workflow

### Archive + Switch Semantics

When creating a new seed while another session is active:

1. Existing session is archived to `sessions/{session_id}.json`
2. New session is created and activated
3. Both sessions are preserved; you can resume the archived one later

## Output

Created seed artifacts in `.tf/knowledge/topics/{topic-id}/`:
- overview.md
- seed.md
- success-metrics.md
- assumptions.md
- constraints.md
- mvp-scope.md
- sources.md

Session state (when activated):
- `.tf/knowledge/.active-planning.json` - Active session pointer
- `.tf/knowledge/sessions/{session_id}.json` - Archived sessions

## Next Steps

After creating seed:
- Review and refine artifacts
- Run `/tf-spike <topic>` to research the idea (auto-links to session)
- Run `/tf-plan <topic>` to create an implementation plan (auto-links to session)
- Run `/tf-backlog <topic>` to create tickets (completes and deactivates session)
