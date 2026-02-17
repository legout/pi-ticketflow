# pi-tk-workflow

IRF workflow toolkit for Pi: ticket management, agent orchestration, and review loops.

```
Implement -> Review -> Fix -> Close
```

## Quick Intro

`pi-tk-workflow` helps you run ticket work in a consistent loop:

1. Capture context (`seed`, `plan`, `spike`, `baseline`)
2. Generate/maintain tickets
3. Execute implementation with structured reviews
4. Apply fixes and close with artifacts
5. Optionally run autonomous processing via Ralph

## Feature Overview

- Ticket-first development workflow (`/tf`, `/tf-next`, `/ralph-start`)
- Planning and research commands (`/tf-plan`, `/tf-seed`, `/tf-spike`, `/tf-baseline`)
- Prompt chaining plan flow (`/tf-plan-chain`)
- Backlog generation and maintenance (`/tf-backlog`, `/tf-tags-suggest`, `/tf-deps-sync`)
- Agent-driven quality loop (parallel reviewers + fixer + closer)
- Persistent knowledge base under `.tf/knowledge/`
- Project-scoped workflow assets under `agents/`, `prompts/`, `skills/`, and `.tf/`

See detailed capabilities in [`docs/features.md`](docs/features.md).

## Getting Started

### 1. Prerequisites

- [`pi`](https://github.com/mariozechner/pi)
- `tk` CLI in `PATH`
- Python 3.9+

### 2. Install CLI

**From GitHub (users):**
```bash
uvx --from git+https://github.com/legout/pi-ticketflow tf install --global
```

**From local clone (developers):**
```bash
git clone https://github.com/legout/pi-ticketflow.git
cd pi-ticketflow
uvx --from . tf install --global
```

See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed options.

### 3. Set Up Global Pi Environment

```bash
tf setup
```

### 4. Initialize a Project

```bash
cd /path/to/project
tf init
tf sync
```

### 5. Configure (Optional)

Configure models and workflow settings interactively:

```bash
tf config              # Interactive wizard
tf config --list       # Show current config
tf config --set metaModels.worker.model=kimi-coding/k2p5
```

### 6. Update

Update the CLI and workflow assets:

```bash
tf self-update         # Update CLI to latest version
tf update              # Update project workflow assets
tf sync                # Re-sync after changes
```

### 7. Run First Workflow

```bash
/tf-seed "Build a CLI tool for managing migrations"
/tf-backlog <seed-topic-id>
/tf <ticket-id>
```

Optional autonomous loop:

```bash
/ralph-start --max-iterations 10
```

For full setup and practical walkthroughs, see [`docs/getting-started.md`](docs/getting-started.md).

## Documentation

- [`docs/README.md`](docs/README.md): documentation index
- [`docs/getting-started.md`](docs/getting-started.md): installation and first workflow
- [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md): detailed installation (GitHub vs local)
- [`NEW_COMMANDS.md`](NEW_COMMANDS.md): `tf self-update` and `tf config` guide
- [`docs/features.md`](docs/features.md): feature details and capabilities
- [`docs/commands.md`](docs/commands.md): command reference
- [`docs/workflows.md`](docs/workflows.md): end-to-end workflow guides
- [`docs/configuration.md`](docs/configuration.md): config model and settings
- [`docs/architecture.md`](docs/architecture.md): system architecture and layout
- [`docs/ralph.md`](docs/ralph.md): Ralph loop operations
- [`docs/deprecation-policy.md`](docs/deprecation-policy.md): active deprecations and migration policy

## Package Namespace Migration

The canonical Python package is `tf`. `tf_cli` remains a compatibility shim during the 0.4.x line and is planned for removal in 0.5.0.

Migration details: [`docs/deprecation-policy.md`](docs/deprecation-policy.md)

## Workflow Status

- ✅ IRF workflow chain validated (pt-gydg)
- ✅ Implement → Review → Fix → Close cycle operational
