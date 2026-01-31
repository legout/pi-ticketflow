# Skill-Based Refactoring Plan for pi-tk-workflow

## Executive Summary

This document outlines a refactoring from slash commands to a skill-based architecture using the `pi-prompt-template-model` extension. Commands become thin wrappers that reference skills via frontmatter, enabling automatic model switching and skill injection.

## Current Architecture Analysis

### Current Structure
```
prompts/                    # Commands (prompt templates)
├── irf.md                  # /irf (6-8 subagents)
├── irf-lite.md             # /irf-lite (3 subagents) - RECOMMENDED
├── irf-seed.md / irf-seed-lite.md
├── irf-backlog.md / irf-backlog-lite.md
├── irf-spike.md / irf-spike-lite.md
├── irf-baseline.md / irf-baseline-lite.md
├── irf-followups.md / irf-followups-lite.md
├── irf-from-openspec.md / irf-from-openspec-lite.md
└── irf-sync.md

agents/                     # Subagent definitions
├── implementer.md
├── reviewer-general.md
├── reviewer-spec-audit.md
├── reviewer-second-opinion.md
├── review-merge.md
├── fixer.md
├── closer.md
├── researcher.md
├── researcher-fetch.md
└── irf-planner.md

workflows/implement-review-fix-close/
└── config.json             # Model & workflow configuration
```

### Current Command Count: 17 prompts
- 2 core workflows (`/irf`, `/irf-lite`)
- 12 planning workflows (6 original + 6 lite)
- 1 sync command (`/irf-sync`)
- Plus Ralph loop commands

## Proposed Architecture

### Core Principles

1. **Skills Contain Expertise**: Skills are the source of truth for domain knowledge
2. **Commands are Thin Wrappers**: Commands specify `model` and `skill` in frontmatter
3. **Agents Remain Separate**: Subagent files (`implementer.md`, etc.) stay as-is - they're execution units, not skills
4. **Extension Handles Orchestration**: `pi-prompt-template-model` manages model switching and skill injection

### Skill Hierarchy

```
skills/                     # Domain expertise
├── irf-workflow/           # Core IRF implementation cycle
│   └── SKILL.md
├── irf-planning/           # Research & planning activities
│   └── SKILL.md
├── irf-config/             # Setup, sync, maintenance
│   └── SKILL.md
└── ralph/                  # Autonomous loop orchestration
    └── SKILL.md

prompts/                    # Thin command wrappers (frontmatter only)
├── irf.md
├── irf-lite.md
├── irf-seed.md
├── irf-backlog.md
├── irf-spike.md
├── irf-baseline.md
├── irf-followups.md
├── irf-from-openspec.md
├── irf-sync.md
└── ralph-start.md

agents/                     # Subagent definitions (unchanged)
├── implementer.md
├── reviewer-general.md
└── ... (unchanged)
```

## Skill Definitions

### 1. irf-workflow (Core Implementation)

**Purpose**: Execute the Implement → Review → Fix → Close cycle

**When to Use**: Any ticket implementation, whether standalone or in a loop

**Key Capabilities**:
- Re-anchor context (read AGENTS.md, lessons learned)
- Optional research using MCP tools
- Implementation with model-switch pattern
- Parallel review orchestration (subagent spawning)
- Review merge and issue deduplication
- Fix application with quality checks
- Ticket closure with progress tracking
- Ralph integration (lessons extraction, progress tracking)

**Model Strategy**:
- Implementation: Strong model (Sonnet, Kimi-K2.5)
- Review merge/Fix: Cheap model (GLM-4.7)
- Closure: Cheap model

**Command Mapping**:
| Command | Model | Skill | Notes |
|---------|-------|-------|-------|
| `/irf` | `chutes/moonshotai/Kimi-K2.5-TEE:high` | `irf-workflow` | Full workflow with all subagents |
| `/irf-lite` | `chutes/moonshotai/Kimi-K2.5-TEE:high` | `irf-workflow` | Simplified, uses model-switch |

**Why Combined?**
The skill contains the full workflow knowledge. The distinction between `/irf` and `/irf-lite` is in execution strategy (subagent nesting depth), not domain expertise. Both use the same patterns.

---

### 2. irf-planning (Research & Planning)

**Purpose**: Upstream activities - capture ideas, research, create tickets

**When to Use**: Before implementation - when defining what to build

**Key Capabilities**:
- Seed capture (idea → structured artifacts)
- Backlog generation (seed → small tickets)
- Research spikes (sequential or parallel)
- Baseline capture (brownfield analysis)
- Follow-up ticket creation
- OpenSpec bridge

**Model Strategy**:
- All activities: Cheap, fast model (GPT-5.1 Codex Mini, GLM-4.7)

**Command Mapping**:
| Command | Model | Skill | Notes |
|---------|-------|-------|-------|
| `/irf-seed` | `gpt-5.1-codex-mini` | `irf-planning` | Lite version recommended |
| `/irf-backlog` | `gpt-5.1-codex-mini` | `irf-planning` | Lite version recommended |
| `/irf-spike` | `gpt-5.1-codex-mini` | `irf-planning` | With --parallel flag support |
| `/irf-baseline` | `gpt-5.1-codex-mini` | `irf-planning` | Project scanning |
| `/irf-followups` | `gpt-5.1-codex-mini` | `irf-planning` | Parse reviews → tickets |
| `/irf-from-openspec` | `gpt-5.1-codex-mini` | `irf-planning` | Bridge to OpenSpec |

**Why Combined?**
All planning activities share:
- Same model requirements (cheap, fast)
- Same artifact structure (knowledge base)
- Same pattern (model-switch, execute inline, write artifacts)
- Similar tool usage (file I/O, `tk` CLI)

---

### 3. irf-config (Setup & Maintenance)

**Purpose**: Installation, configuration, synchronization

**When to Use**: Setup, updating models, verifying installation

**Key Capabilities**:
- Verify extensions installed (`pi-subagents`, `pi-model-switch`)
- Sync models from config to agent files
- Verify/check MCP server configuration
- Generate model aliases

**Model Strategy**:
- Cheapest/fastest model (GLM-4.7) - this is administrative work

**Command Mapping**:
| Command | Model | Skill | Notes |
|---------|-------|-------|-------|
| `/irf-sync` | `zai/glm-4.7` | `irf-config` | Sync config → agents |

---

### 4. ralph (Autonomous Loop)

**Purpose**: Orchestrate autonomous ticket processing

**When to Use**: Running multiple tickets without manual intervention

**Key Capabilities**:
- Initialize Ralph directory structure
- Load and apply lessons learned
- Track progress across iterations
- Output promise sigils for loop detection
- Prune old lessons
- Monitor loop status

**Model Strategy**:
- Same as workflow (delegates to `/irf-lite`)

**Command Mapping**:
| Command | Model | Skill | Notes |
|---------|-------|-------|-------|
| `/ralph-start` | (none - uses current) | `ralph` | `restore: false` to stay in loop |
| `/ralph-status` | `zai/glm-4.7` | `ralph` | Quick status check |
| `/ralph-reset` | `zai/glm-4.7` | `ralph` | Reset progress |

**Why Separate Skill?**
Ralph is about orchestration, not implementation. It manages:
- State across tickets
- Lessons learned synthesis
- Loop termination conditions

This is distinct domain knowledge from the workflow itself.

---

## Command Wrapper Examples

### /irf-lite (Recommended Workflow)

```markdown
---
description: Implement ticket with simplified IRF workflow (Implement → Review → Fix → Close)
model: chutes/moonshotai/Kimi-K2.5-TEE:high
skill: irf-workflow
---
Execute the IRF workflow for ticket: $@

Parse the ticket ID and flags from arguments, then follow the irf-workflow skill instructions.
```

### /irf-seed

```markdown
---
description: Capture a greenfield idea into seed artifacts
model: openai-codex/gpt-5.1-codex-mini
skill: irf-planning
---
Create seed artifacts for idea: $@

Follow the "Seed Capture" procedure from the irf-planning skill.
```

### /irf-spike

```markdown
---
description: Research spike on a topic
model: openai-codex/gpt-5.1-codex-mini
skill: irf-planning
---
Run research spike on topic: $@

Follow the "Research Spike" procedure from the irf-planning skill.
Use --parallel flag if specified for parallel subagent fetching.
```

### /irf-sync

```markdown
---
description: Sync IRF workflow configuration
model: zai/glm-4.7
skill: irf-config
---
Sync configuration from config.json to agent files.

Follow the "Configuration Sync" procedure from the irf-config skill.
```

### /ralph-start

```markdown
---
description: Start autonomous ticket processing loop
skill: ralph
restore: false
---
Start Ralph loop for autonomous ticket processing.

Follow the "Autonomous Loop" procedure from the ralph skill.
Process tickets until max iterations or backlog empty.
```

---

## File Structure After Refactoring

```
pi-tk-workflow/
├── skills/
│   ├── irf-workflow/
│   │   └── SKILL.md          # Core workflow expertise
│   ├── irf-planning/
│   │   └── SKILL.md          # Planning & research expertise
│   ├── irf-config/
│   │   └── SKILL.md          # Setup & sync expertise
│   └── ralph/
│       └── SKILL.md          # Autonomous loop expertise
│
├── prompts/                   # Thin wrappers with frontmatter
│   ├── irf.md
│   ├── irf-lite.md
│   ├── irf-seed.md
│   ├── irf-backlog.md
│   ├── irf-spike.md
│   ├── irf-baseline.md
│   ├── irf-followups.md
│   ├── irf-from-openspec.md
│   ├── irf-sync.md
│   ├── ralph-start.md
│   └── ralph-status.md
│
├── agents/                    # Unchanged - subagent definitions
│   ├── implementer.md
│   ├── reviewer-general.md
│   ├── reviewer-spec-audit.md
│   ├── reviewer-second-opinion.md
│   ├── review-merge.md
│   ├── fixer.md
│   ├── closer.md
│   ├── researcher.md
│   ├── researcher-fetch.md
│   └── irf-planner.md
│
├── workflows/
│   └── implement-review-fix-close/
│       └── config.json        # Model configuration
│
└── bin/
    └── irf                    # CLI tool (unchanged)
```

---

## Migration Path

### Phase 1: Create Skills (Parallel to Existing)
1. Create `skills/irf-workflow/SKILL.md` with full workflow knowledge
2. Create `skills/irf-planning/SKILL.md` with planning procedures
3. Create `skills/irf-config/SKILL.md` with setup/sync procedures
4. Create `skills/ralph/SKILL.md` with loop orchestration

### Phase 2: Create Thin Command Wrappers
1. Add frontmatter to existing prompt files:
   - `model:` field from config
   - `skill:` field mapping to appropriate skill
   - `description:` for autocomplete
2. Remove duplicate content (now in skills)
3. Keep only invocation parsing and delegation

### Phase 3: Deprecate Originals
1. Move original heavy prompts to `prompts/legacy/`
2. Keep thin wrappers in `prompts/`
3. Update README with new architecture

### Phase 4: Optimize (Future)
- Consider removing `-lite` suffix since thin wrappers are inherently "lite"
- `/irf` → Full workflow with model-switch (formerly /irf-lite)
- `/irf-deep` → Full workflow with all subagents (formerly /irf)

---

## Benefits of This Architecture

1. **DRY**: Workflow knowledge lives in one place per domain
2. **Composability**: Skills can be combined (e.g., planning → workflow)
3. **Model Optimization**: Each command declares optimal model in frontmatter
4. **Skill Injection**: Full skill content loaded into context automatically
5. **Auto-Restore**: Extension handles model restoration after command completes
6. **Maintainability**: Change workflow logic in one place (skill), affects all commands
7. **Discoverability**: `/irf` autocomplete shows `[+irf-workflow]` indicating skill injection

---

## Extension Requirements

Required Pi extensions:
```bash
pi install npm:pi-prompt-template-model   # Entry model switch via frontmatter
pi install npm:pi-subagents               # Parallel review subagents
pi install npm:pi-model-switch            # Runtime model switches between workflow phases
```

**Extension Roles:**

| Extension | Purpose |
|-----------|---------|
| `pi-prompt-template-model` | Reads `model:`/`skill:` frontmatter when command starts, switches to initial model, injects skill content |
| `pi-model-switch` | Workflow skill uses this internally to switch models between phases (implement → review merge → fix) |
| `pi-subagents` | Spawns parallel reviewer subagents during the review phase |

Both `pi-prompt-template-model` and `pi-model-switch` are required - they handle model switching at different times (entry vs runtime).

Optional:
```bash
pi install npm:pi-mcp-adapter             # MCP tools for research
pi install npm:pi-review-loop             # Post-execution review
```

---

## Open Questions

1. **Original vs Lite**: Should we keep both `/irf` and `/irf-lite` as separate commands, or consolidate with flags?
   - Recommendation: Keep both for flexibility, but document `/irf-lite` as recommended

2. **Skill Granularity**: Should `irf-research` be separate from `irf-planning`?
   - Recommendation: No - research is integral to planning, not used standalone

3. **Agent-to-Skill Migration**: Should subagents (`implementer.md`, etc.) become skills?
   - Recommendation: No - they're execution units spawned by the workflow skill, not independent capabilities

4. **Config Access**: How do skills access `config.json`?
   - Answer: Skills reference it by path (project → global), same as current prompts

---

## Summary

| Before | After |
|--------|-------|
| 17 heavy prompt files | 4 skills + 11 thin wrappers |
| Duplicate workflow knowledge | Single source of truth per domain |
| Manual model switching | Automatic via extension |
| Optional skill loading | Forced skill injection via frontmatter |
| Commands define everything | Skills define expertise, commands define entry points |

This refactoring maintains all current functionality while improving maintainability, clarity, and leveraging modern Pi extension capabilities.
