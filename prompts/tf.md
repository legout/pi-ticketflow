---
description: Execute IRF workflow via /chain-prompts (Research → Implement → Review → Fix → Close)
model: kimi-coding/k2p5
thinking: medium
skill: tf-workflow
---

# /tf

Execute the complete IRF (Implement → Review → Fix → Close) workflow for a ticket **using `/chain-prompts`**.

## Input Arguments
- `$1` - Ticket ID (e.g., `pt-9hgu`)
- `$@` - All arguments including flags

## Flags
| Flag | Description |
|------|-------------|
| `--no-research` | Skip research phase, start at implement |
| `--with-research` | Force research phase (default if enabled) |
| `--no-clarify` | Auto-approve clarifications |
| `--auto` | Enable auto mode (passes through to phases) |
| `--plan` / `--dry-run` | Show execution plan, don't execute |
| `--retry-reset` | Reset retry escalation state |

## Execution Procedure (use `/chain-prompts`)

### Step 1: Resolve Entry Phase

Determine whether to include `tf-research`:
- Default: Check `.tf/config/settings.json` → `workflow.enableResearcher`
- If `true` or `--with-research`: include `tf-research`
- If `--no-research`: start at `tf-implement`

### Step 2: Build Chain

**With research:**
```
/chain-prompts tf-research -> tf-implement -> tf-review -> tf-fix -> tf-close -- $@
```

**Without research:**
```
/chain-prompts tf-implement -> tf-review -> tf-fix -> tf-close -- $@
```

### Step 3: Execute Chain

**IMPORTANT: `/chain-prompts` is a Pi slash command (in-session), NOT a bash command.**

To execute the chain, issue it directly as a Pi slash command in the current session. Do **not** run it via the bash tool and do **not** wrap it in a bash code block.

**Correct behavior:**
- Build the chain command from flags
- Output the `/chain-prompts ...` command directly so Pi executes it

**Wrong behavior:**
- Running `/chain-prompts ...` in bash
- Running `pi "/chain-prompts ..."`
- Spawning subprocesses for chain execution

### Step 4: Review Phase

The `tf-review` phase runs **parallel subagent reviewers** (see `tf-review-phase` skill).

### Step 5: Post-Chain Actions (Optional)

If flags present:
- `--create-followups`: Run `/tf-followups` on review output
- `--simplify-tickets`: Run ticket simplification
- `--final-review-loop`: Start review loop

## Artifact Directory

`.tf/knowledge/tickets/{ticket-id}/`

## Notes

- Requires `pi-prompt-template-model` extension to provide `/chain-prompts`.
- Each phase uses its own prompt with model/thinking frontmatter.
- All execution happens in the current Pi session (no subprocesses).