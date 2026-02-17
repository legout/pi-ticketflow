# Getting Started

## Prerequisites

- [`pi`](https://github.com/mariozechner/pi)
- `tk` ticket CLI in `PATH`
- Python 3.9+
- `uvx` (recommended installer/runtime)

## Installation

### Method 1: Install from GitHub (Recommended for Users)

#### Quick Install (One Line)

```bash
uvx --from git+https://github.com/legout/pi-ticketflow tf install --global
```

#### Full Setup

```bash
# 1. Install CLI globally
uvx --from git+https://github.com/legout/pi-ticketflow tf install --global

# 2. Setup Pi extensions and MCP
/tf setup

# 3. Go to your project
cd /path/to/your/project

# 4. Initialize tf in the project
tf init

# 5. Sync configuration
tf sync
```

Alternative (legacy installer script):

```bash
curl -fsSL https://raw.githubusercontent.com/legout/pi-ticketflow/main/install.sh | bash -s -- --global
```

#### Updating from GitHub

```bash
# Update the CLI itself
tf self-update

# Update project workflow assets
tf update

# Re-sync after updates
tf sync
```

### Method 2: Install from Local Clone (Developers/Contributors)

#### Clone and Install

```bash
# 1. Clone the repository
git clone https://github.com/legout/pi-ticketflow.git
cd pi-ticketflow

# 2. Install from local repo
uvx --from . tf install --global

# 3. Record the local repo (optional, for development)
echo "$(pwd)" > ~/.tf/cli-root
```

#### Development Workflow

When developing, you have several options to run without reinstalling:

```bash
# Option A: Run directly from repo (no install needed)
uvx --from . tf --help
uvx --from . tf init
uvx --from . tf self-update

# Option B: Use Python directly (fastest for development)
python -m tf.cli --help
python -m tf.cli init
python -m tf.cli self-update

# Option C: After installing, use the global tf command
tf --help
tf init
tf self-update
```

#### Updating from Local Clone

```bash
# Pull latest changes
git pull

# Re-install to update the CLI
cd pi-ticketflow
uvx --from . tf install --global

# Or just run directly without reinstall
uvx --from . tf update
uvx --from . tf sync
```

### Installation Comparison

| Scenario | From GitHub | From Local Clone |
|----------|-------------|------------------|
| **Install** | `uvx --from git+https://... tf install --global` | `uvx --from . tf install --global` |
| **Run once** | Same as install | `uvx --from . tf <command>` |
| **Update CLI** | `tf self-update` | `git pull && uvx --from . tf install --global` |
| **Update assets** | `tf update` | `uvx --from . tf update` |
| **Development** | Not recommended | `python -m tf.cli <command>` |
| **Auto-update** | Yes, via `self-update` | No, manual git pull |

### Environment Variables

For advanced use cases, you can control the source with environment variables:

```bash
# Use custom repo
cd /path/to/pi-ticketflow
export TF_REPO_ROOT="$(pwd)"
tf --help  # Uses local repo

# Use custom uvx source
export TF_UVX_FROM="git+https://github.com/yourfork/pi-ticketflow"
tf self-update  # Updates from your fork
```

### Troubleshooting

#### Command not found after install

```bash
# Check if ~/.local/bin is in PATH
echo $PATH | grep ".local/bin"

# Add to PATH if missing
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Using wrong version (development issue)

```bash
# Check which tf is being used
which tf
cat ~/.tf/cli-root  # Shows recorded repo root
cat ~/.tf/cli-source  # Shows recorded uvx source

# Clear recorded sources to use default
rm ~/.tf/cli-root ~/.tf/cli-source
```

#### Self-update from local clone

If you installed from a local clone, `tf self-update` will try to update from the default GitHub repo, not your local changes. For development:

```bash
# Don't use self-update for local development
git pull  # Get latest
uvx --from . tf install --global  # Re-install from local
```

## Global Setup

Configure Pi extensions and optional MCP/web search integration:

```bash
tf setup
```

Required extensions:

```bash
pi install npm:pi-prompt-template-model
pi install npm:pi-subagents
```

Optional:

```bash
pi install npm:pi-review-loop
pi install npm:pi-mcp-adapter
pi install npm:pi-web-access
```

## Project Setup

In each project where you want TF workflow assets:

```bash
cd /path/to/project
tf init
tf sync
```

This creates/updates:

- `.pi/agents/`, `.pi/prompts/`, `.pi/skills/` (Pi workflow assets)
- `.tf/config`, `.tf/knowledge`, `.tf/ralph` (TF state and config)

## First End-to-End Run

1. Capture idea/context:

```bash
/tf-seed "Build a CLI tool for managing database migrations"
```

2. Generate backlog from the seed:

```bash
/tf-backlog <seed-topic-id>
```

Use the topic id returned by `/tf-seed` (for example, `seed-build-a-cli-tool`).

3. Execute one ticket:

```bash
/tf <ticket-id>
```

For deterministic orchestration debugging (optional):

```bash
tf irf <ticket-id> --plan
```

4. Optional autonomous execution:

```bash
/ralph-start --max-iterations 10
```

## Common Next Commands

- `/tf-next` - get next ready ticket
- `/tf-plan-chain "<request>"` - run full plan consult/revise/review loop
- `/tf-tags-suggest --apply` - fill missing `component:*` tags
- `/tf-deps-sync --apply` - align dependency edges
- `tf doctor` - diagnose environment/config issues

## Where to Go Next

- Command details: [`commands.md`](commands.md)
- Workflow selection: [`workflows.md`](workflows.md)
- Configuration tuning: [`configuration.md`](configuration.md)
- Architecture: [`architecture.md`](architecture.md)
