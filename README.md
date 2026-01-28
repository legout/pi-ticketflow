# pi-tk-workflow

A reusable Pi workflow package for ticket implementation:

**Implement → Review → Fix → Close**

This package bundles the agents, prompts, and workflow config used by the `/implement-review-fix-close` command.

---

## What’s included

```
agents/
  implementer.md
  reviewer-general.md
  reviewer-spec-audit.md
  reviewer-second-opinion.md
  review-merge.md
  fixer.md
  closer.md
  researcher.md
  researcher-fetch.md
  simplifier.md
  simplify-ticket.md

prompts/
  implement-review-fix-close.md
  irfc-sync.md

workflows/implement-review-fix-close/
  config.json
  README.md
```

---

## Prerequisites

- Pi installed and configured
- Ticket CLI: `tk` in PATH
- Language tools you intend to use (see workflow README)

### Required Pi extensions

```bash
pi install npm:pi-subagents
pi install npm:pi-interactive-shell
```

### Optional but recommended

```bash
pi install npm:pi-review-loop
pi install npm:pi-mcp-adapter
```

### Optional MCP servers

If you want MCP tools, install the MCP adapter and configure servers:

Required for MCP:
```bash
pi install npm:pi-mcp-adapter
```

Optional MCP servers (used by the research step):
- exa
- context7
- grep_app
- zai web search
- zai web reader
- zai vision

ZAI MCP servers require an API key. Context7/exa can run without a key, but a key is recommended for higher limits.

> Tip: Run `./bin/irfc setup` to install extensions and configure MCP interactively.

---

## Installation

### Interactive setup (recommended)

```bash
./bin/irfc setup
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
- `~/.pi/agent/prompts`
- `~/.pi/agent/workflows/implement-review-fix-close`

For extensions/MCP, use `./bin/irfc setup`.

### Project install (files only)

```bash
./install.sh --project /path/to/project
```

Installs into:
- `/path/to/project/.pi/agents`
- `/path/to/project/.pi/prompts`
- `/path/to/project/.pi/workflows/implement-review-fix-close`

Project settings override global settings.

For extensions/MCP, use `./bin/irfc setup`.

---

## Usage

```
/implement-review-fix-close <ticket-id> [flags]
```

Optional research step (if enabled) stores knowledge in:
```
.pi/knowledge/
  topics/
  tickets/<ticket-id>.md
```

See `workflows/implement-review-fix-close/README.md` for flags, configuration, and optional tools.

---

## CLI

### Commands

```bash
./bin/irfc setup   # interactive install + extensions + MCP
./bin/irfc sync    # sync models from config into agent files
```

Use `--global` or `--project <path>` to target a specific scope.

## Updating models

Edit `workflows/implement-review-fix-close/config.json` and run:

```
/irfc-sync
```

Or from the repo:
```bash
./bin/irfc sync
```

---

## Notes

- Config is read at runtime by the prompt and implementer agent.
- Models are applied via `/irfc-sync` (updates agent frontmatter).
- MCP config is written to `<target>/.pi/mcp.json` or `~/.pi/agent/mcp.json` when you run `./bin/irfc setup` and enable MCP.
