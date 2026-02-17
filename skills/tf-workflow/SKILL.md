---
name: tf-workflow
description: Orchestrate the Implement → Review → Fix → Close workflow using /chain-prompts in the same Pi session.
---

# TF Workflow Skill

Orchestration skill for the IRF (Implement → Review → Fix → Close) cycle. The `/tf` command **must** use `/chain-prompts` and run entirely within the **same Pi session**.

## Requirements

- `pi-prompt-template-model` extension installed (provides `/chain-prompts`)
- Phase prompts exist with model/thinking frontmatter

## Phase Prompts

| Phase | Prompt | Skill | Model Source |
|-------|--------|-------|--------------|
| Research | `tf-research` | `tf-research` | frontmatter in `prompts/tf-research.md` |
| Implement | `tf-implement` | `tf-implement` | frontmatter in `prompts/tf-implement.md` |
| Review | `tf-review` | `tf-review-phase` | frontmatter in `prompts/tf-review.md` |
| Fix | `tf-fix` | `tf-fix` | frontmatter in `prompts/tf-fix.md` |
| Close | `tf-close` | `tf-close` | frontmatter in `prompts/tf-close.md` |

## Flag Resolution

**Research entry decision:**
```
if --no-research: skip to implement
if --with-research: force research
else: check workflow.enableResearcher in settings.json
```

**Passthrough flags** (passed to all phases):
- `--auto`
- `--no-clarify`
- `--retry-reset`

**Dry-run flags** (stop after planning):
- `--plan`
- `--dry-run`

**Post-chain flags** (run after main chain):
- `--create-followups`
- `--simplify-tickets`
- `--final-review-loop`

## Chain Construction

**With research:**
```
/chain-prompts tf-research -> tf-implement -> tf-review -> tf-fix -> tf-close -- $@
```

**Without research:**
```
/chain-prompts tf-implement -> tf-review -> tf-fix -> tf-close -- $@
```

## Review Phase (Parallel Subagents)

The review phase launches 3 reviewers concurrently (via `subagent` tool):

```json
{
  "agentScope": "project",
  "tasks": [
    {"agent": "reviewer-general", "task": "{ticket}", "cwd": "{repoRoot}"},
    {"agent": "reviewer-spec-audit", "task": "{ticket}", "cwd": "{repoRoot}"},
    {"agent": "reviewer-second-opinion", "task": "{ticket}", "cwd": "{repoRoot}"}
  ]
}
```

Then merges with `review-merge` agent.

## Artifact Directory

`.tf/knowledge/tickets/{ticket-id}/`

## How to Execute `/chain-prompts`

**CRITICAL: `/chain-prompts` is a Pi slash command (in-session), NOT a bash/shell command.**

When the agent executes a chain, it must output `/chain-prompts ...` directly so Pi handles it as a slash command.

Do **not**:
- run `/chain-prompts` via bash
- wrap `/chain-prompts` in a bash code block
- run `pi "/chain-prompts ..."`

## No Subprocess Rule

- **Do not** call `tf irf` or spawn `pi -p` subprocesses
- **Do not** wrap `/chain-prompts` in bash commands
- `/chain-prompts` must be output directly for Pi to execute
- Phases are driven by prompt frontmatter (model/thinking/skill)
