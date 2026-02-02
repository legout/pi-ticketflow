# Command Reference

Complete reference for all pi-tk-workflow commands.

---

## Implementation Commands

### `/irf`

Execute the Implement → Review → Fix → Close workflow on a ticket.

```
/irf <ticket-id> [--auto] [--no-research] [--with-research] [--plan]
                 [--create-followups] [--simplify-tickets] [--final-review-loop]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `ticket-id` | Ticket identifier (e.g., `abc-123`) |
| `--auto` / `--no-clarify` | Run headless (no confirmation prompts) |
| `--no-research` | Skip research step |
| `--with-research` | Force enable research step |
| `--plan` / `--dry-run` | Show resolved chain and exit |
| `--create-followups` | Create follow-up tickets after review |
| `--simplify-tickets` | Run simplify on created tickets |
| `--final-review-loop` | Run `/review-start` after chain |

**Workflow:**
1. Re-anchor context (load AGENTS.md, lessons, ticket)
2. Research (optional, MCP tools)
3. Implement (model-switch to implementer model)
4. Parallel reviews (3 subagents)
5. Merge reviews (deduplication)
6. Fix issues
7. Follow-ups (optional)
8. Close ticket
9. Ralph integration (if active)

**Output Artifacts:**
- `implementation.md` - Implementation summary
- `review.md` - Consolidated review
- `fixes.md` - Fixes applied
- `close-summary.md` - Final summary
- `.pi/ralph/progress.md` - Updated (if Ralph active)

---

### `/ralph-start`

Start autonomous ticket processing loop.

```
/ralph-start [--max-iterations N]
```

Processes tickets until backlog is empty, max iterations reached, or error occurs.

**Features:**
- Re-anchors context per ticket
- Reads lessons from `.pi/ralph/AGENTS.md`
- Updates progress in `.pi/ralph/progress.md`
- Outputs `<promise>COMPLETE</promise>` on finish

---

## Planning Commands

### `/irf-plan`

Create a plan document from a request.

```
/irf-plan <request description>
```

Creates a structured plan in `.pi/knowledge/topics/plan-*/`:
- `plan.md` - Single source of truth
- Status starts as `draft`

**Example:**
```
/irf-plan Refactor auth flow to support OAuth + magic links
```

**Next Steps:**
```
/irf-plan-consult plan-auth-refactor
/irf-plan-revise plan-auth-refactor
/irf-plan-review plan-auth-refactor --high-accuracy
```

---

### `/irf-plan-consult`

Review a plan for gaps, ambiguities, and over-engineering.

```
/irf-plan-consult <plan-id-or-path>
```

Updates the same `plan.md` with Consultant Notes and sets status to `consulted`.

---

### `/irf-plan-revise`

Revise a plan based on consultant/reviewer feedback.

```
/irf-plan-revise <plan-id-or-path>
```

Updates the same `plan.md` with revisions and sets status to `revised`.

---

### `/irf-plan-review`

Validate a plan with high-accuracy checks.

```
/irf-plan-review <plan-id-or-path> [--high-accuracy]
```

Updates `plan.md` with PASS/FAIL status:
- `status: approved` if passes
- `status: blocked` if fails

---

## Research Commands

### `/irf-seed`

Capture an idea into structured seed artifacts.

```
/irf-seed <idea description>
```

**Creates artifacts in `.pi/knowledge/topics/seed-*/`:**
- `overview.md` - Summary + keywords
- `seed.md` - Vision, concept, features, questions
- `success-metrics.md` - How to measure success
- `assumptions.md` - Technical/user/business assumptions
- `constraints.md` - Limitations and boundaries
- `mvp-scope.md` - What's in/out of MVP
- `sources.md` - Source tracking

**Example:**
```
/irf-seed Build a CLI tool for managing database migrations
```

**Next Steps:**
```
/irf-backlog seed-build-a-cli
```

---

### `/irf-spike`

Research spike on a topic.

```
/irf-spike <topic> [--parallel]
```

**Modes:**
| Mode | Description |
|------|-------------|
| Sequential (default) | Query tools one by one |
| Parallel (`--parallel`) | Spawn 3 subagents simultaneously |

**Creates artifacts in `.pi/knowledge/topics/spike-*/`:**
- `overview.md` - Summary + quick answer
- `spike.md` - Full analysis with findings, options, recommendation
- `sources.md` - All URLs and tools used

**Example:**
```
/irf-spike "React Server Components vs Next.js App Router"
/irf-spike "PostgreSQL partitioning strategies" --parallel
```

---

### `/irf-baseline`

Capture status-quo of an existing project.

```
/irf-baseline [focus-area]
```

**Creates artifacts in `.pi/knowledge/topics/baseline-*/`:**
- `overview.md` - Project summary
- `baseline.md` - Architecture, components, entry points
- `risk-map.md` - Technical, dependency, knowledge risks
- `test-inventory.md` - Test structure and gaps
- `dependency-map.md` - Dependencies and external services
- `sources.md` - Files scanned

**Examples:**
```
/irf-baseline
/irf-baseline "authentication system"
```

**Next Steps:**
```
/irf-backlog baseline-myapp
```

---

## Ticket Creation Commands

### `/irf-backlog`

Create tickets from seeds, baselines, or plans.

```
/irf-backlog <seed|baseline|plan>
```

Generates 5-15 small tickets:
- **30 lines or less** in description
- **1-2 hours** estimated work
- **Self-contained** - no need to load full planning docs
- **Linked** via `external-ref` to source topic

**Ticket templates vary by source:**
- **Seed**: Includes context, acceptance criteria, constraints, seed reference
- **Baseline**: Includes risk/test context, baseline reference
- **Plan**: Includes plan context, work plan reference

**Examples:**
```
/irf-backlog seed-build-a-cli
/irf-backlog baseline-myapp
/irf-backlog plan-auth-rewrite
```

**Output:**
- Tickets created in `tk`
- `backlog.md` written to topic directory

---

### `/irf-backlog-ls`

List backlog status and tickets.

```
/irf-backlog-ls [topic-id-or-path]
```

**Without topic:** Lists all seed/baseline/plan topics with backlog status
**With topic:** Shows full backlog table + summary

**Example:**
```
/irf-backlog-ls
/irf-backlog-ls seed-build-a-cli
```

---

### `/irf-followups`

Create follow-up tickets from review warnings/suggestions.

```
/irf-followups <review-path-or-ticket-id>
```

Creates tickets from:
- **Warnings** - Technical debt (should address)
- **Suggestions** - Improvements (nice to have)

Both are out of scope for the original ticket.

**Example:**
```
/irf-followups ./review.md
/irf-followups abc-1234
```

---

### `/irf-from-openspec`

Create tickets from an OpenSpec change.

```
/irf-from-openspec <change-id-or-path>
```

Reads OpenSpec artifacts:
- `tasks.md` (required)
- `proposal.md`, `design.md` (for context)

Creates tickets tagged with `openspec` and linked via `external-ref`.

**Example:**
```
/irf-from-openspec auth-pkce-support
/irf-from-openspec openspec/changes/auth-pkce-support/
```

---

## Configuration Commands

### `/irf-sync`

Sync configuration from `config.json` to agent and prompt files.

```
/irf-sync
```

Updates `model:` frontmatter in all agent and prompt files based on `workflows/implement-review-fix-close/config.json`.

---

## CLI Reference

The `irf` CLI is installed during setup and provides utilities for workflow management.

### Global Install (CLI at `~/.local/bin/irf`)

```bash
# Setup
irf setup                          # Interactive install + extensions + MCP

# Sync
irf sync                           # Sync models from config

# Diagnostics
irf doctor                         # Preflight checks

# Backlog
irf backlog-ls [topic]             # List backlog status

# Track changes
irf track <path>                   # Append to files_changed.txt

# Ralph Loop
irf ralph init                     # Create .pi/ralph/ directory
irf ralph status                   # Show current loop state
irf ralph reset                    # Clear progress
irf ralph reset --keep-lessons     # Clear progress, keep lessons
irf ralph lessons                  # Show lessons learned
irf ralph lessons prune 20         # Keep only last 20 lessons

# AGENTS.md Management
irf agentsmd init                  # Create minimal AGENTS.md
irf agentsmd status                # Show AGENTS.md overview
irf agentsmd validate              # Check for bloat, stale paths
irf agentsmd fix                   # Auto-fix common issues
```

### Project Install (CLI at `.pi/bin/irf`)

Use `./.pi/bin/irf` instead of `irf` for project installs.

```bash
./.pi/bin/irf setup
./.pi/bin/irf sync
./.pi/bin/irf ralph init
```
