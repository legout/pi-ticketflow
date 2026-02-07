---
id: pt-az2p
status: closed
deps: [pt-ynqf]
links: []
created: 2026-02-07T12:36:41Z
type: task
priority: 1
assignee: legout
external-ref: plan-critical-cleanup-simplification
tags: [tf, cleanup, plan, component:docs, component:cli]
---
# CLN-09: Define deprecation policy and timeline for tf legacy / tf new namespaces

## Task
Publish deprecation policy for legacy CLI namespaces before removal.

## Context
Immediate hard removal is risky without explicit compatibility policy.

## Acceptance Criteria
- [ ] Policy doc with timeline and milestones
- [ ] Communication notes for users
- [ ] Clear criteria for final removal

## Constraints
- Must precede hard removal ticket

## References
- Plan: plan-critical-cleanup-simplification



## Notes

**2026-02-07T15:57:49Z**

## Implementation Complete

Created comprehensive deprecation policy document at .

### Deliverables
- **Policy document** with timeline and milestones (3 phases: Notice → Soft Deprecation → Hard Removal)
- **Communication strategy** covering users, internal team, and migration support
- **Removal criteria checklist** for all three artifact categories

### Key Dates
- **2026-02-07**: Policy effective (today)
- **2026-03-01**: Ticketflow (new Python CLI)

Usage:
  tf new agentsmd <subcommand> [path]
  tf new backlog-ls [topic-id-or-path]
  tf new doctor [--project <path>] [--fix]
  tf new init [--project <path>]
  tf new login [--project <path>] [--global]
  tf new next [--project <path>]
  tf new priority-reclassify [--apply] [--ids ...] [--ready] [--status ...] [--tag ...]
  tf new ralph <subcommand> [options]
  tf new setup [--project <path>] [--global]
  tf new sync [--project <path>] [--global]
  tf new tags-classify <text> [--json] [--rationale]
  tf new tags-keywords
  tf new tags-suggest [--ticket <id>] [title] [--json] [--rationale]
  tf new track <path> [--file <files_changed_path>]
  tf new update [--project <path>] [--global]

Commands:
  agentsmd            AGENTS.md management (init/status/validate/fix/update)
  backlog-ls          List backlog status for seed/baseline/plan topics
  doctor              Preflight checks for tk/pi/extensions/checkers
  init                Create .tf project scaffolding
  login               Configure API keys for web search and MCP servers
  next                Print the next ready ticket id
  priority-reclassify Reclassify ticket priorities using P0-P4 rubric
  ralph               Python implementation of Ralph loop (start/run)
  setup               Install Pi/TF assets and extensions
  sync                Sync model frontmatter from config
  tags-classify       Classify text and suggest component tags
  tags-keywords       Show keyword mapping for component classification
  tags-suggest        Suggest component tags for a ticket
  track               Append a file to files_changed.txt
  update              Download latest agents/skills/prompts prefix removal target
- **2026-03-15**:  suffix removal target
- **2026-04-01**: Ticketflow CLI

Usage:
  tf setup [--global|--project <path>]
  tf init [--project <path>]
  tf login [--global|--project <path>]
  tf sync [--project <path>]
  tf update [--global|--project <path>]
  tf doctor [--project <path>]
  tf next [--project <path>]
  tf backlog-ls [topic-id-or-path] [--project <path>]
  tf track <path> [--file <files_changed_path>]
  tf seed [--active|--sessions [seed-id]|--resume <id>]
  tf ralph <subcommand> [options]

Commands:
  setup       Install Pi assets + optional dependencies + MCP config
  init        Scaffold .tf/ directories (config, knowledge, ralph)
  login       Configure API keys (Perplexity, Context7, Exa, ZAI)
  sync        Sync agent models from workflow config into agent files
  update      Download latest agents, skills, and prompts
  doctor      Preflight checks for tk/pi/extensions/checkers/version
              Options: --fix (auto-fix VERSION file), --dry-run (show changes)
  next        Print the next open and ready ticket id
  backlog-ls  List backlog status and tickets for seed/baseline topics
  track       Append file paths to files_changed.txt (deduped)
  seed        Planning session management (active, sessions, resume)
  ralph       Ralph loop management (see below)
  agentsmd    AGENTS.md management (init, validate, fix, status)

Seed Subcommands:
  seed --active              Print current active session or "none"
  seed --sessions [seed-id]  List archived sessions, optionally filtered
  seed --resume <id>         Resume session by seed-id or session-id

Ralph Subcommands:
  ralph init     Create .tf/ralph/ directory structure
  ralph status   Show current loop state and statistics
  ralph reset    Clear progress (optionally keep lessons)
  ralph lessons  Show or prune lessons learned
  ralph start    Run loop via pi -p (uses /tf)
  ralph run      Run one ticket via pi -p (uses /tf)

Agentsmd Subcommands:
  agentsmd init [path]     Create minimal AGENTS.md (defaults: uv, current dir)
  agentsmd status [path]   Show AGENTS.md overview and recommendations
  agentsmd validate [path] Check for bloat, stale paths, contradictions
  agentsmd fix [path]      Auto-fix common issues (backup created)

Options:
  --version, -v, -V        Print version and exit
  --global                 Install/sync Pi files in ~/.pi/agent (setup/login only)
  --project <path>         Operate on project at <path> (uses <path>/.pi + <path>/.tf)
  --file <path>            Output files_changed.txt path (track only)
  --keep-lessons           Keep lessons when resetting (ralph reset only)
  --help                   Show this help

Environment (for setup MCP):
  ZAI_API_KEY, CONTEXT7_API_KEY, EXA_API_KEY, PERPLEXITY_API_KEY

Environment (for track):
  TF_FILES_CHANGED, TF_CHAIN_DIR removal target

### Review Results
- Critical: 0
- Major: 1 (fixed - header format)
- Minor: 6 (2 fixed, 4 acknowledged)
- Warnings: 5 (follow-up tickets)
- Suggestions: 7 (future enhancements)

### Commit
- Hash: a618f6d
- Files: docs/deprecation-policy.md (347 lines)

### Next Steps
- pt-g42s (CLN-10) is unblocked for legacy shell runtime removal per policy timeline
