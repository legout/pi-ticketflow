# Skill-Based Refactoring Summary

## Overview

This refactoring transforms pi-tk-workflow from a command-heavy architecture to a **skill-centric** architecture using the `pi-prompt-template-model` extension. Commands become thin wrappers with `model:` and `skill:` frontmatter, while skills contain the actual domain expertise.

## What Was Created

### 4 Core Skills (in `skills/`)

| Skill | Purpose | Lines | Key Procedures |
|-------|---------|-------|----------------|
| `irf-workflow` | Core IRF implementation cycle | ~300 | Re-anchor, Research, Implement, Review, Fix, Close, Ralph Integration |
| `irf-planning` | Research & planning activities | ~350 | Seed Capture, Backlog Generation, Research Spike, Baseline, Follow-ups, OpenSpec Bridge |
| `irf-config` | Setup & maintenance | ~200 | Verify Setup, Sync Models, Generate Aliases, Verify MCP |
| `ralph` | Autonomous loop orchestration | ~250 | Initialize, Start Loop, Extract Lessons, Update Progress, Prune |

**Total skill content: ~1100 lines** of dense, reusable expertise.

### 10 Thin Command Wrappers (in `prompts/*-new.md`)

| Command | Model | Skill | Lines |
|---------|-------|-------|-------|
| `/irf` | Kimi-K2.5 | irf-workflow | ~70 |
| `/irf-lite` | Kimi-K2.5 | irf-workflow | ~75 |
| `/irf-seed` | GPT-5.1-mini | irf-planning | ~50 |
| `/irf-backlog` | GPT-5.1-mini | irf-planning | ~55 |
| `/irf-spike` | GPT-5.1-mini | irf-planning | ~70 |
| `/irf-baseline` | GPT-5.1-mini | irf-planning | ~55 |
| `/irf-followups` | GPT-5.1-mini | irf-planning | ~65 |
| `/irf-from-openspec` | GPT-5.1-mini | irf-planning | ~60 |
| `/irf-sync` | GLM-4.7 | irf-config | ~85 |
| `/ralph-start` | (current) | ralph | ~80 |

**Total command content: ~625 lines** of thin wrappers (vs ~12,000 lines in original prompts).

## Architecture Comparison

### Before (Current)
```
prompts/
├── irf.md (1500 lines)          - Full workflow description
├── irf-lite.md (1500 lines)     - Simplified workflow
├── irf-seed.md (600 lines)      - Seed capture
├── irf-backlog.md (600 lines)   - Backlog generation
├── irf-spike.md (800 lines)     - Research spike
├── irf-baseline.md (600 lines)  - Baseline capture
├── irf-followups.md (700 lines) - Follow-up creation
├── irf-from-openspec.md (700 lines) - OpenSpec bridge
└── irf-sync.md (900 lines)      - Config sync

Total: ~8,000 lines of duplicated/exploded workflow knowledge
```

### After (New)
```
skills/
├── irf-workflow/SKILL.md (~300) - Workflow expertise (ONE place)
├── irf-planning/SKILL.md (~350) - Planning expertise (ONE place)
├── irf-config/SKILL.md (~200)   - Config expertise (ONE place)
└── ralph/SKILL.md (~250)        - Loop expertise (ONE place)

prompts/
├── irf.md (~70)                 - Frontmatter only
├── irf-lite.md (~75)            - Frontmatter only
├── irf-seed.md (~50)            - Frontmatter only
└── ... (7 more, similar)

Total: ~1,100 lines skills + ~625 lines wrappers = ~1,725 lines
```

**Reduction: ~78% less code** with clearer separation of concerns.

## Key Benefits

1. **DRY**: Workflow knowledge lives in one place per domain
2. **Auto Model Management**: Extension switches models via `model:` frontmatter
3. **Skill Injection**: `skill:` frontmatter forces skill loading
4. **Composability**: Skills can be combined and reused
5. **Maintainability**: Change logic in one place, all commands benefit
6. **Clarity**: Commands show their dependencies in autocomplete

## How It Works

1. User types `/irf-lite ABC-123`
2. Extension reads frontmatter:
   ```yaml
   model: chutes/moonshotai/Kimi-K2.5-TEE:high
   skill: irf-workflow
   ```
3. Extension switches to Kimi-K2.5 model
4. Extension injects `skills/irf-workflow/SKILL.md` into system prompt
5. Command body executes (parses arguments, delegates to skill)
6. After completion, extension restores original model

## Migration Path

### Phase 1: Add Skills (Current)
- ✅ Skills created in `skills/`
- ✅ New command wrappers created as `prompts/*-new.md`
- Existing commands unchanged (100% backward compatible)

### Phase 2: Parallel Usage
- Install `pi-prompt-template-model` extension
- Test new commands alongside old ones
- Validate identical outputs

### Phase 3: Cutover
- Rename `prompts/*.md` → `prompts/legacy/*.md`
- Rename `prompts/*-new.md` → `prompts/*.md`
- Update documentation

### Phase 4: Cleanup (Future)
- Remove legacy prompts
- Consider consolidating `/irf` and `/irf-lite` (they use same skill)

## Extension Requirements

Required:
```bash
pi install npm:pi-prompt-template-model  # NEW - entry model switch via frontmatter
pi install npm:pi-subagents              # EXISTING - parallel reviews
pi install npm:pi-model-switch           # EXISTING - runtime switching between phases
```

**Why two model-switch extensions?**

| Extension | When | Purpose |
|-----------|------|---------|
| `pi-prompt-template-model` | Command entry | Reads `model:`/`skill:` frontmatter, switches to initial model |
| `pi-model-switch` | During workflow | Runtime switches between phases (implement → review → fix) |

The workflow skill internally calls `switch_model` to move between implementation, review merge, and fix phases. Both extensions are required for full functionality.

## Files Created

```
docs/
├── skill-refactoring-plan.md   # Detailed design document
├── migration-to-skills.md      # Migration guide for users/contributors
└── SKILL_REFACTORING_SUMMARY.md # This file

skills/
├── irf-workflow/SKILL.md       # Core implementation workflow
├── irf-planning/SKILL.md       # Research & planning procedures
├── irf-config/SKILL.md         # Setup & sync procedures
└── ralph/SKILL.md              # Autonomous loop procedures

prompts/
├── irf-new.md                  # Thin wrapper (model: Kimi-K2.5)
├── irf-lite-new.md             # Thin wrapper (model: Kimi-K2.5)
├── irf-seed-new.md             # Thin wrapper (model: GPT-5.1-mini)
├── irf-backlog-new.md          # Thin wrapper (model: GPT-5.1-mini)
├── irf-spike-new.md            # Thin wrapper (model: GPT-5.1-mini)
├── irf-baseline-new.md         # Thin wrapper (model: GPT-5.1-mini)
├── irf-followups-new.md        # Thin wrapper (model: GPT-5.1-mini)
├── irf-from-openspec-new.md    # Thin wrapper (model: GPT-5.1-mini)
├── irf-sync-new.md             # Thin wrapper (model: GLM-4.7)
└── ralph-start-new.md          # Thin wrapper (skill: ralph)
```

## Model Strategy by Domain

| Domain | Model | Why |
|--------|-------|-----|
| **Workflow** | Kimi-K2.5 / Sonnet | Deep reasoning for implementation |
| **Planning** | GPT-5.1-mini | Fast, cheap for planning tasks |
| **Config** | GLM-4.7 | Cheapest for admin tasks |
| **Ralph** | (inherits) | Delegates to workflow model |

## Design Decisions

### Why 4 Skills (Not More)?

- **irf-workflow**: Core implementation is a single domain
- **irf-planning**: All planning activities share model/tooling patterns
- **irf-config**: Administrative work is distinct from execution
- **ralph**: Orchestration is distinct from implementation

### Why Not Make Agents Into Skills?

Agents (`implementer.md`, `reviewer-general.md`, etc.) are **execution units**, not capabilities:
- They're spawned as subagents
- They don't contain reusable expertise
- They're already the right abstraction

### Why Combine Planning Commands Into One Skill?

All planning commands share:
- Same model requirements (cheap, fast)
- Same artifact structure (knowledge base)
- Same pattern (model-switch → execute inline → write artifacts)
- Similar tool usage (file I/O, `tk` CLI)

### Why Keep `/irf` And `/irf-lite` Separate?

They use the same skill but different execution strategies:
- `/irf`: Spawns subagents for each phase
- `/irf-lite`: Uses model-switch for sequential phases

Keeping both lets users choose their reliability/parallelism tradeoff.

## Future Opportunities

1. **Model Aliases**: Define aliases like `model: irf-implementer` in config
2. **Skill Parameters**: Pass flags to skills via command body
3. **Conditional Skills**: Load different skills based on project type
4. **Skill Composition**: Chain skills (planning → workflow → ralph)
5. **Dynamic Models**: Choose model based on ticket complexity

## Conclusion

This refactoring achieves:
- **Lean**: 78% reduction in code
- **Simple**: Clear separation of concerns
- **Powerful**: Reusable skills, automatic model management
- **Backward Compatible**: Existing commands continue working

The architecture now aligns with Pi's modern extension ecosystem while maintaining the proven IRF workflow semantics.
