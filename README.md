# pi-tk-workflow

A reusable Pi workflow package for ticket implementation:

**Implement → Review → Fix → Close**

This package bundles the agents, skills, prompts, and workflow config used by the `/irf` and `/irf-lite` commands.

---

## What's included

```
agents/                         # Subagent execution units
  implementer.md                # Core implementation agent
  reviewer-general.md           # General code review
  reviewer-spec-audit.md        # Specification audit
  reviewer-second-opinion.md    # Second opinion review
  fixer.md                      # Fix identified issues
  closer.md                     # Close ticket and summarize

skills/                         # Domain expertise (skills inject into context)
  irf-workflow/SKILL.md         # Core IRF implementation workflow
  irf-planning/SKILL.md         # Research & planning activities
  irf-config/SKILL.md           # Setup & configuration
  ralph/SKILL.md                # Autonomous loop orchestration

prompts/                        # Command entry points (thin wrappers)
  irf.md                        # Full workflow with subagents
  irf-lite.md                   # Recommended - uses model-switch
  irf-seed.md                   # Capture ideas into seed artifacts
  irf-backlog.md                # Create tickets from seeds
  irf-spike.md                  # Research spike
  irf-baseline.md               # Capture project baseline
  irf-followups.md              # Create tickets from review warnings
  irf-from-openspec.md          # Bridge from OpenSpec
  irf-sync.md                   # Sync configuration
  ralph-start.md                # Start autonomous loop

workflows/implement-review-fix-close/
  config.json                   # Model & workflow configuration
  README.md                     # Workflow-specific docs

docs/
  SKILL_REFACTORING_SUMMARY.md  # Architecture overview
  migration-to-skills.md        # Migration guide
  subagent-simplification.md    # Subagent reduction analysis
```

---

## Architecture

This package uses a **skill-centric** architecture:

1. **Skills** contain domain expertise (`skills/*/SKILL.md`)
2. **Commands** are thin wrappers with `model:` and `skill:` frontmatter
3. **Agents** are execution units spawned by skills for parallel work

### How it works

```
User types: /irf-lite ABC-123

1. Extension reads frontmatter:
   model: chutes/moonshotai/Kimi-K2.5-TEE:high
   skill: irf-workflow

2. Switches to specified model
3. Injects skill content into system prompt
4. Executes command body
```

---

## Prerequisites

- Pi installed and configured
- Ticket CLI: `tk` in PATH
- Language tools you intend to use (see workflow README)

### Required Pi extensions

```bash
pi install npm:pi-prompt-template-model  # Entry model switch via frontmatter
pi install npm:pi-model-switch           # Runtime model switching
pi install npm:pi-subagents              # Parallel reviewer subagents
```

**Extension roles:**
- `pi-prompt-template-model` - Reads `model:` and `skill:` frontmatter, handles initial model switch
- `pi-model-switch` - Runtime model switches during workflow (implement → review → fix)
- `pi-subagents` - Spawns parallel reviewer subagents

### Optional extensions

```bash
pi install npm:pi-review-loop    # Post-chain review with /review-start
pi install npm:pi-mcp-adapter    # MCP tools for research step
```

### Optional MCP servers

For research steps, install the MCP adapter and configure servers:

```bash
pi install npm:pi-mcp-adapter
```

Available MCP servers:
- context7 - documentation search
- exa - web search
- grep_app - code search
- zai web search / zai web reader / zai vision (requires API key)

> Tip: Run `./bin/irf setup` to install extensions and configure MCP interactively.

---

## Installation

### Interactive setup (recommended)

```bash
./bin/irf setup
```

This guides you through:
- global vs project install
- optional extensions
- MCP server configuration + API keys

### Global install (files only)

```bash
./install.sh --global
```

Installs into:
- `~/.pi/agent/agents`
- `~/.pi/agent/skills`
- `~/.pi/agent/prompts`
- `~/.pi/agent/workflows/implement-review-fix-close`

### Project install (files only)

```bash
./install.sh --project /path/to/project
```

Installs into:
- `/path/to/project/.pi/agents`
- `/path/to/project/.pi/skills`
- `/path/to/project/.pi/prompts`
- `/path/to/project/.pi/workflows/implement-review-fix-close`

---

## Usage

### Implementation Workflows

```bash
# Recommended - uses model-switch for sequential phases
/irf-lite <ticket-id> [--auto] [--no-research] [--with-research]

# Full workflow - uses subagents for each phase
/irf <ticket-id> [flags]
```

### Planning Workflows

```bash
/irf-seed <idea>                  # Capture idea into seed artifacts
/irf-backlog <seed-path>          # Create tickets from seed
/irf-spike <topic> [--parallel]   # Research spike
/irf-baseline [focus]             # Capture brownfield status quo
/irf-followups <review-path>      # Create follow-up tickets
/irf-from-openspec <change-id>    # Bridge from OpenSpec
```

### Configuration

```bash
/irf-sync                         # Sync models from config
```

### Ralph Loop

```bash
/ralph-start [--max-iterations 50]  # Start autonomous processing
```

### Flags

| Flag | Description |
|------|-------------|
| `--auto` / `--no-clarify` | Run headless (no confirmation prompts) |
| `--no-research` | Skip research step |
| `--with-research` | Force enable research step |
| `--parallel` | Use parallel subagents for research (/irf-spike only) |

---

## CLI

### Commands

```bash
./bin/irf setup   # Interactive install + extensions + MCP
./bin/irf sync    # Sync models from config into agent files
./bin/irf doctor  # Preflight checks for tools and extensions
```

### Ralph Loop Commands

```bash
./bin/irf ralph init                  # Create .pi/ralph/ directory
./bin/irf ralph status                # Show current loop state
./bin/irf ralph reset                 # Clear progress and lessons
./bin/irf ralph reset --keep-lessons  # Clear progress, keep lessons
./bin/irf ralph lessons               # Show lessons learned
./bin/irf ralph lessons prune 20      # Keep only last 20 lessons
```

### Updating models

Edit `workflows/implement-review-fix-close/config.json` and run:

```bash
/irf-sync
# or
./bin/irf sync
```

---

## Workflow Flows

### `/irf-lite` flow (recommended)

```
┌─────────────────────────────────────────────────────────────┐
│  MAIN AGENT                                                 │
├─────────────────────────────────────────────────────────────┤
│  0. Research (optional, sequential, no subagent)            │
│  1. Implement (model-switch to implementer model)           │
├─────────────────────────────────────────────────────────────┤
│  2. SUBAGENT: Parallel Reviews ← Only subagent step         │
│     ├─ reviewer-general                                     │
│     ├─ reviewer-spec-audit                                  │
│     └─ reviewer-second-opinion                              │
├─────────────────────────────────────────────────────────────┤
│  3. Merge reviews (model-switch to cheap model)             │
│  4. Fix issues (same cheap model)                           │
│  5. Close ticket                                            │
│  6. Learn & Track (updates .pi/ralph/ if active)            │
└─────────────────────────────────────────────────────────────┘
```

**Ralph-Ready**: Automatically loads lessons from `.pi/ralph/AGENTS.md` and tracks progress.

### `/irf` flow (subagent-based)

```
researcher (optional subagent)
    ↓
implementer (subagent)
    ↓
┌─ reviewer-general ──────┐
├─ reviewer-spec-audit ───┼─ (parallel subagents)
└─ reviewer-second-opinion┘
    ↓
review-merge (main agent)
    ↓
fixer (main agent)
    ↓
closer (main agent)
```

### Planning workflows

```
┌─────────────────────────────────────────────────────────────┐
│  MAIN AGENT                                                 │
├─────────────────────────────────────────────────────────────┤
│  1. model-switch to planning model (cheap)                  │
│  2. Execute planning task inline                            │
│  3. Write artifacts to knowledge base                       │
│  4. [spike only, --parallel] Optional parallel research     │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### Ralph-Ready by Default

`/irf-lite` is designed for autonomous operation:

- **Re-anchoring**: Reads `AGENTS.md` and `.pi/ralph/AGENTS.md` at start
- **Lessons Learned**: Synthesizes and appends lessons after each ticket
- **Progress Tracking**: Updates `.pi/ralph/progress.md` automatically
- **Promise Sigil**: Outputs `<promise>TICKET_XXX_COMPLETE</promise>` for loop detection

Works standalone or in a Ralph loop—no configuration needed.

### Small, Self-Contained Tickets

Planning workflows (`/irf-backlog`, `/irf-from-openspec`) create:

- **30 lines or less** per ticket description
- **1-2 hours** estimated work
- **Self-contained context** - no need to load full planning docs
- **Summarized constraints** from original specs

---

## Model Strategy

Models are configured in `workflows/implement-review-fix-close/config.json`:

| Role | Default Model | Purpose |
|------|---------------|---------|
| implementer | Kimi-K2.5 / Sonnet | Deep reasoning for implementation |
| reviewer-* | GPT-5.1-mini | Fast, capable review |
| review-merge | GPT-5.1-mini | Deduplication and consolidation |
| fixer | GLM-4.7 | Cheap fixes |
| closer | GLM-4.7 | Cheap summarization |

Run `/irf-sync` after editing config to apply changes.

---

## Ralph Loop (Autonomous Processing)

The Ralph Loop enables autonomous ticket processing with re-anchoring and lessons learned.

### Concept

```
┌──────────────────────────────────────────────────────────────┐
│  RALPH LOOP                                                  │
├──────────────────────────────────────────────────────────────┤
│  while tickets remain:                                       │
│    1. RE-ANCHOR: Read .pi/ralph/AGENTS.md (lessons learned)  │
│    2. PICK: Get next ready ticket from backlog               │
│    3. EXECUTE: Run /irf-lite <ticket> --auto                 │
│    4. LEARN: Append lessons to .pi/ralph/AGENTS.md           │
│    5. TRACK: Update .pi/ralph/progress.md                    │
│    6. PROMISE: Output <promise>COMPLETE</promise> when done  │
└──────────────────────────────────────────────────────────────┘
```

### Files

```
.pi/ralph/
├── AGENTS.md      # Lessons learned (read by implementer for re-anchoring)
├── progress.md    # Loop state and ticket history
└── config.json    # Loop configuration (max iterations, queries, etc.)
```

### Setup

```bash
# Initialize Ralph directory
./bin/irf ralph init

# Check status
./bin/irf ralph status

# Start loop in Pi
/ralph-start --max-iterations 50
```

### Key Principles

1. **Re-anchoring**: Each iteration starts fresh, reading lessons from `.pi/ralph/AGENTS.md`
2. **Lessons Learned**: The closer synthesizes discoveries and appends them for future iterations
3. **Progress Tracking**: External state in `.pi/ralph/progress.md` survives context resets
4. **Promise Sigil**: Loop terminates when `<promise>COMPLETE</promise>` is output

---

## Skills Reference

### irf-workflow

Core implementation workflow. Contains procedures for:
- Re-anchor context (loading lessons, knowledge)
- Research (optional, MCP tools)
- Implement (model-switch)
- Parallel reviews (subagent orchestration)
- Merge reviews (deduplication)
- Fix issues (quality checks)
- Close ticket (tk integration)
- Ralph integration (progress, lessons)

### irf-planning

Research & planning activities. Contains procedures for:
- Seed capture (idea → artifacts)
- Backlog generation (seed → tickets)
- Research spike (sequential/parallel)
- Baseline capture (project analysis)
- Follow-up creation (review → tickets)
- OpenSpec bridge (spec → tickets)

### irf-config

Setup & maintenance. Contains procedures for:
- Verifying extensions installed
- Syncing models to agent files
- Generating model aliases
- Checking MCP configuration

### ralph

Autonomous loop orchestration. Contains procedures for:
- Initializing Ralph directory
- Starting autonomous loop
- Extracting lessons
- Updating progress
- Pruning old lessons

---

## Notes

- Config is read at runtime by the skills
- Models are applied via `/irf-sync` (updates agent frontmatter)
- MCP config is written to `<target>/.pi/mcp.json` when you run `./bin/irf setup`
- All workflows write artifacts to current working directory
