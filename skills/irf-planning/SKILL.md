---
name: irf-planning
description: Research and planning activities for IRF workflow. Use for capturing ideas, creating tickets, research spikes, and bridging from external specs. Includes seed capture, backlog generation, baseline analysis, and OpenSpec integration.
---

# IRF Planning Skill

Expertise for upstream planning activities - everything that happens BEFORE implementation.

## When to Use This Skill

- Capturing a new feature idea
- Researching a technical topic
- Creating implementation tickets from seeds/specs
- Analyzing an existing codebase (baseline)
- Creating follow-up tickets from reviews

## Key Principle: Small, Self-Contained Tickets

All ticket creation in this skill follows these rules:
- **30 lines or less** in description
- **1-2 hours** estimated work
- **Self-contained** - includes all needed context
- **Single responsibility** - one feature per ticket

## Configuration

Read workflow config (project overrides global):
- `.pi/workflows/implement-review-fix-close/config.json`
- `~/.pi/agent/workflows/implement-review-fix-close/config.json`

Extract `workflow.knowledgeDir` (default: `.pi/knowledge`).

## Execution Procedures

### Procedure: Seed Capture

**Purpose**: Capture a greenfield idea into structured artifacts.

**Input**: Idea description (from user)

**Steps**:

1. **Create topic ID**:
   - Lowercase, replace spaces with dashes
   - Max 40 characters
   - Prefix with `seed-`
   - Example: "Build a CLI" → `seed-build-a-cli`

2. **Create directory**:
   ```bash
   mkdir -p "{knowledgeDir}/topics/{topic-id}"
   ```

3. **Write artifacts**:

   **overview.md**:
   ```markdown
   # {topic-id}
   Brief 2-3 sentence summary.

   ## Keywords
   - keyword1
   - keyword2
   ```

   **seed.md**:
   ```markdown
   # Seed: {idea}

   ## Vision
   What problem does this solve?

   ## Core Concept
   High-level solution description

   ## Key Features
   1. Feature one
   2. Feature two

   ## Open Questions
   - Question 1?
   ```

   **success-metrics.md**, **assumptions.md**, **constraints.md**, **mvp-scope.md**, **sources.md**

4. **Update index.json**:
   ```json
   {
     "id": "{topic-id}",
     "title": "{idea title}",
     "keywords": ["keyword1"],
     "overview": "topics/{topic-id}/overview.md",
     "sources": "topics/{topic-id}/sources.md"
   }
   ```

**Output**: Topic directory with seed artifacts

---

### Procedure: Backlog Generation

**Purpose**: Create small, actionable tickets from a seed.

**Input**: Seed topic-id or path

**Steps**:

1. **Locate seed**:
   - If path provided: use directly
   - If topic-id: `{knowledgeDir}/topics/{topic-id}/`
   - Auto-locate if only one seed exists

2. **Read seed artifacts**:
   - `seed.md` (required)
   - `mvp-scope.md`, `success-metrics.md`, `constraints.md` (if exist)

3. **Create tickets** (5-15 small tickets):

   For each ticket, use this template:
   ```markdown
   ## Task
   <Single-sentence description>

   ## Context
   <2-3 sentences summarizing relevant context>

   ## Acceptance Criteria
   - [ ] <criterion 1>
   - [ ] <criterion 2>
   - [ ] <criterion 3>

   ## Constraints
   - <relevant constraint>

   ## References
   - Seed: <topic-id>
   ```

4. **Create via `tk`**:
   ```bash
   tk create "<title>" \
     --description "<description>" \
     --tags irf,backlog \
     --type task \
     --priority 2
   ```

5. **Write backlog.md**:
   ```markdown
   # Backlog: {topic-id}
   | ID | Title | Est. Hours |
   |----|-------|------------|
   | {id} | {title} | 1-2 |
   ```

---

### Procedure: Research Spike

**Purpose**: Research a topic and store findings.

**Input**: Topic to research, optional `--parallel` flag

**Steps**:

1. **Create topic ID**:
   - Lowercase, replace spaces with dashes
   - Max 40 characters
   - Prefix with `spike-`

2. **Check MCP tools**:
   - context7 (documentation)
   - exa (web search)
   - grep_app (code search)
   - zai-web-search (alternative search)

3. **Research**:

   **Sequential mode** (default):
   - Query each available tool one by one
   - Synthesize in main agent

   **Parallel mode** (`--parallel` flag):
   ```json
   {
     "tasks": [
       {"agent": "researcher-fetch", "task": "Docs: {topic}"},
       {"agent": "researcher-fetch", "task": "Web: {topic}"},
       {"agent": "researcher-fetch", "task": "Code: {topic}"}
     ]
   }
   ```

4. **Write artifacts**:

   **overview.md**: Summary + keywords
   **sources.md**: All URLs and tools used
   **spike.md**: Full analysis with findings, options, recommendation

---

### Procedure: Baseline Capture

**Purpose**: Document status-quo of existing project.

**Input**: Optional focus area

**Steps**:

1. **Determine topic ID**:
   ```bash
   repo_name=$(basename $(pwd))
   topic_id="baseline-${repo_name}"
   ```

2. **Scan project**:
   - Read: README.md, package.json, etc.
   - Find entry points: `find . -name "main.*" -o -name "app.*"`
   - Find tests: `find . -type d -name "test*"`

3. **Write artifacts**:
   - **overview.md**: Summary
   - **baseline.md**: Architecture, components, entry points
   - **risk-map.md**: Technical, dependency, knowledge risks
   - **test-inventory.md**: Test directories, commands, coverage gaps
   - **dependency-map.md**: Runtime/dev dependencies, external services
   - **sources.md**: Files scanned

---

### Procedure: Follow-up Creation

**Purpose**: Create tickets from review Warnings/Suggestions.

**Input**: Path to review.md or ticket ID

**Steps**:

1. **Resolve review path**:
   - If path: use directly
   - If ticket ID: search `/tmp/pi-chain-runs` for matching review
   - If empty: use `./review.md` if exists

2. **Parse review**:
   - Extract Warnings section
   - Extract Suggestions section

3. **Create ticket per item**:
   ```bash
   tk create "<title>" \
     --description "## Origin\nFrom review of: {ticket}\nFile: {file}\nLine: {line}\n\n## Issue\n{description}" \
     --tags irf,followup \
     --priority 3
   ```

4. **Write followups.md** documenting created tickets

---

### Procedure: OpenSpec Bridge

**Purpose**: Convert OpenSpec change into IRF tickets.

**Input**: Change ID or path

**Steps**:

1. **Locate change**:
   - Look for `openspec/changes/{id}/`
   - Fallback: `changes/{id}/`

2. **Read artifacts**:
   - `tasks.md` (required)
   - `proposal.md`, `design.md` (for context extraction)

3. **Parse tasks**:
   - For each task in tasks.md
   - Extract relevant sections from proposal/design
   - Split large tasks into 1-2 hour chunks

4. **Create tickets** with template:
   ```markdown
   ## Task
   <Specific task>

   ## Context
   <2-3 sentences from OpenSpec>

   ## Technical Details
   <Key decisions affecting this task>

   ## Acceptance Criteria
   - [ ] <criterion 1>
   - [ ] Tests added

   ## Constraints
   <Relevant constraints>

   ## References
   - OpenSpec Change: {change_id}
   ```

5. **Write backlog.md** in change directory

---

## Common Tool Usage

### Model Switching
All procedures use model-switch pattern:
```
switch_model action="switch" search="gpt-5.1-codex-mini"
```

### Ticket Creation Pattern
```bash
tk create "<title>" \
  --description "<markdown description>" \
  --tags irf,<tag> \
  --type task \
  --priority <1-5>
```

### Knowledge Base Structure
```
.pi/knowledge/
├── index.json              # Registry of all topics
├── tickets/
│   └── {ticket-id}.md      # Per-ticket research
└── topics/
    └── {topic-id}/
        ├── overview.md
        ├── seed.md|spike.md|baseline.md
        ├── sources.md
        └── backlog.md
```

## Error Handling

- **Seed not found**: List available seeds and ask user
- **No warnings/suggestions**: Write "No follow-ups needed" and exit
- **OpenSpec not found**: Ask for explicit path
- **tk create fails**: Log error, continue with remaining tickets

## Output Summary

| Procedure | Primary Output | Secondary Output |
|-----------|---------------|------------------|
| Seed Capture | `topics/{id}/` directory | index.json updated |
| Backlog | `backlog.md` | Tickets in `tk` |
| Spike | `topics/{id}/` directory | index.json updated |
| Baseline | `topics/{id}/` directory | index.json updated |
| Follow-ups | `followups.md` | Tickets in `tk` |
| OpenSpec | `backlog.md` | Tickets in `tk` |
