# Migration Guide: Commands to Skills

This guide explains how to migrate from the current prompt-based commands to the new skill-based architecture.

## Overview

The refactoring maintains **100% backward compatibility** while introducing a cleaner architecture:

| Before | After |
|--------|-------|
| 17 heavy prompt files (~1500 lines each) | 4 skills + 11 thin wrappers (~100 lines each) |
| Workflow knowledge duplicated | Single source of truth per domain |
| Manual model management | Automatic via `pi-prompt-template-model` |
| Commands define everything | Skills define expertise, commands define entry points |

## Quick Comparison

### Before (Current)
```markdown
---
description: Simplified IRF workflow
---

# Implement → Review → Fix → Close (Lite)

Full 1500-line workflow description here...

## Step 1: Re-Anchor Context
[100 lines of detailed instructions]

## Step 2: Research
[200 lines of detailed instructions]
...
```

### After (New)
```markdown
---
description: Implement ticket [irf-workflow +Kimi-K2.5]
model: chutes/moonshotai/Kimi-K2.5-TEE:high
skill: irf-workflow
---

# /irf-lite

Execute the simplified IRF workflow for ticket: $@

Follow the **IRF Workflow Skill** procedures.
```

## New Architecture

```
skills/                      # Domain expertise (4 files)
├── irf-workflow/SKILL.md    # Core IRF implementation
├── irf-planning/SKILL.md    # Research & planning
├── irf-config/SKILL.md      # Setup & sync
└── ralph/SKILL.md           # Autonomous loop

prompts/                     # Thin wrappers (11 files)
├── irf.md                   # model: Kimi-K2.5, skill: irf-workflow
├── irf-lite.md              # model: Kimi-K2.5, skill: irf-workflow
├── irf-seed.md              # model: codex-mini, skill: irf-planning
├── irf-backlog.md           # model: codex-mini, skill: irf-planning
├── irf-spike.md             # model: codex-mini, skill: irf-planning
├── irf-baseline.md          # model: codex-mini, skill: irf-planning
├── irf-followups.md         # model: codex-mini, skill: irf-planning
├── irf-from-openspec.md     # model: codex-mini, skill: irf-planning
├── irf-sync.md              # model: GLM-4.7, skill: irf-config
└── ralph-start.md           # skill: ralph, restore: false

agents/                      # Unchanged
├── implementer.md
├── reviewer-*.md
└── ...
```

## Benefits

### 1. DRY (Don't Repeat Yourself)

**Before**: Workflow knowledge duplicated across `/irf`, `/irf-lite`, and variations.

**After**: Single `irf-workflow` skill contains all workflow expertise. Commands reference it.

### 2. Automatic Model Management

**Before**: Prompts contained `switch_model` tool calls inline.

**After**: Extension switches models automatically based on `model:` frontmatter.

### 3. Skill Injection

**Before**: Agent might not load the right skill.

**After**: `skill:` frontmatter forces skill injection into system prompt.

### 4. Clear Separation

| Component | Responsibility |
|-----------|---------------|
| Skill | Domain expertise, procedures, patterns |
| Command | Entry point, argument parsing, model selection |
| Agent | Subagent execution unit |

### 5. Easier Maintenance

Change workflow logic in **one place** (skill), all commands benefit.

## Extension Requirements

The skill-based architecture requires **three** extensions:

```bash
# Required for skill-based commands
pi install npm:pi-prompt-template-model

# Required for workflow execution
pi install npm:pi-subagents
pi install npm:pi-model-switch
```

### Extension Roles

| Extension | When Used | Purpose |
|-----------|-----------|---------|
| `pi-prompt-template-model` | **Command entry** | Reads `model:` and `skill:` frontmatter, switches to initial model, injects skill |
| `pi-model-switch` | **During workflow** | Runtime model switches between phases (implement → review → fix) |
| `pi-subagents` | **During workflow** | Spawns parallel reviewer subagents |

**Why both model extensions?**

- `pi-prompt-template-model` handles the **initial** model switch when you type `/irf-lite` (via frontmatter)
- `pi-model-switch` handles **runtime** model switches during execution (implement phase → cheap model for review merge)

The workflow skill internally calls `switch_model` to move between phases, so both extensions are required.

## Migration Steps

### For Users

**No action required!** Existing commands continue to work.

To use new skill-based commands:
1. Install extension: `pi install npm:pi-prompt-template-model`
2. Restart pi
3. Use commands as normal - they'll use skills automatically

### For Contributors

1. **Edit skills** to change workflow logic:
   - `skills/irf-workflow/SKILL.md` - Implementation workflow
   - `skills/irf-planning/SKILL.md` - Planning procedures
   - `skills/irf-config/SKILL.md` - Setup procedures
   - `skills/ralph/SKILL.md` - Loop orchestration

2. **Edit commands** to change entry points:
   - Modify frontmatter (`model:`, `skill:`)
   - Change argument parsing
   - Update delegation logic

## Command Mapping Reference

| Command | Model | Skill | Notes |
|---------|-------|-------|-------|
| `/irf` | `chutes/moonshotai/Kimi-K2.5-TEE:high` | `irf-workflow` | Full subagent workflow |
| `/irf-lite` | `chutes/moonshotai/Kimi-K2.5-TEE:high` | `irf-workflow` | Model-switch workflow (recommended) |
| `/irf-seed` | `openai-codex/gpt-5.1-codex-mini` | `irf-planning` | Capture ideas |
| `/irf-backlog` | `openai-codex/gpt-5.1-codex-mini` | `irf-planning` | Create tickets |
| `/irf-spike` | `openai-codex/gpt-5.1-codex-mini` | `irf-planning` | Research topic |
| `/irf-baseline` | `openai-codex/gpt-5.1-codex-mini` | `irf-planning` | Document codebase |
| `/irf-followups` | `openai-codex/gpt-5.1-codex-mini` | `irf-planning` | From reviews |
| `/irf-from-openspec` | `openai-codex/gpt-5.1-codex-mini` | `irf-planning` | Bridge from OpenSpec |
| `/irf-sync` | `zai/glm-4.7` | `irf-config` | Sync configuration |
| `/ralph-start` | (none) | `ralph` | `restore: false` - stay in loop |

## Autocomplete Display

With the extension, commands show skill and model in autocomplete:

```
/irf-lite        Implement ticket [irf-workflow +Kimi-K2.5] (user)
/irf-seed        Capture idea [irf-planning +codex-mini] (user)
/irf-sync        Sync config [irf-config +GLM-4.7] (user)
/ralph-start     Autonomous loop [ralph] (user)
```

## Skill Content Overview

### irf-workflow

Contains procedures for:
- Re-anchor context (loading lessons, knowledge)
- Research (optional, MCP tools)
- Implement (model-switch)
- Parallel reviews (subagent orchestration)
- Merge reviews (deduplication)
- Fix issues (quality checks)
- Close ticket (tk integration)
- Ralph integration (progress, lessons)

### irf-planning

Contains procedures for:
- Seed capture (idea → artifacts)
- Backlog generation (seed → tickets)
- Research spike (sequential/parallel)
- Baseline capture (project analysis)
- Follow-up creation (review → tickets)
- OpenSpec bridge (spec → tickets)

### irf-config

Contains procedures for:
- Verifying extensions installed
- Syncing models to agent files
- Generating model aliases
- Checking MCP configuration

### ralph

Contains procedures for:
- Initializing Ralph directory
- Starting autonomous loop
- Extracting lessons
- Updating progress
- Pruning old lessons

## Backward Compatibility

The original prompt files remain functional. The new skill-based commands:
- Use the same agents (`implementer.md`, etc.)
- Read the same config (`config.json`)
- Produce the same outputs
- Work with Ralph loop identically

You can migrate gradually:
1. Keep old commands working
2. Add new skill-based commands alongside
3. Test and validate
4. Eventually deprecate old commands

## FAQ

**Q: Do I need to change how I use the commands?**
A: No. Usage is identical. The extension handles model switching and skill injection automatically.

**Q: Can I still customize models?**
A: Yes. Edit `config.json` and run `/irf-sync` - same as before.

**Q: What if the extension isn't installed?**
A: Commands fall back to current behavior (without automatic model switching).

**Q: Can I use skills without the extension?**
A: Yes, via `/skill:irf-workflow` command, but you lose automatic model management.

**Q: Should agents (implementer.md, etc.) become skills?**
A: No. They're execution units spawned by the workflow skill, not independent capabilities.

**Q: Why combine planning commands into one skill?**
A: They share: model requirements, artifact structure, tool usage patterns, and inline execution.

## Troubleshooting

**Extension not found:**
```bash
pi install npm:pi-prompt-template-model
# Restart pi
```

**Skill not loading:**
- Check skill is in `skills/{name}/SKILL.md`
- Verify frontmatter has `name:` and `description:`
- Run `pi` and check for skill loading errors

**Model not switching at command start:**
- Verify `pi-prompt-template-model` extension installed
- Check frontmatter has valid `model:` field
- Restart pi after installing extension

**Model not switching during workflow:**
- Verify `pi-model-switch` extension installed
- Check model ID is valid in config.json
- Check `switch_model` tool is available
