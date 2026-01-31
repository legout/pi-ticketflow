---
name: irf-workflow
description: Execute the Implement → Review → Fix → Close workflow for ticket implementation. Use when implementing any ticket, whether standalone or in a Ralph loop.
---

# IRF Workflow Skill

Core expertise for the Implement → Review → Fix → Close cycle.

## When to Use This Skill

- Implementing a ticket from your backlog
- Processing tickets in a Ralph autonomous loop
- Any code change requiring review and quality checks

## Prerequisites

Before executing, verify:
1. `tk` CLI is available: `which tk`
2. `switch_model` tool is available (from `pi-model-switch` extension)
3. `subagent` tool is available (from `pi-subagents` extension)
4. Ticket exists: `tk show <ticket-id>` succeeds

### Extension Requirements

This skill requires two Pi extensions:

| Extension | Purpose |
|-----------|---------|
| `pi-prompt-template-model` | **Entry model switch** - Sets the initial model via frontmatter when the command starts |
| `pi-model-switch` | **Runtime model switches** - Changes models between workflow phases (implement → review → fix) |

Install both:
```bash
pi install npm:pi-prompt-template-model
pi install npm:pi-model-switch
```

## Configuration

Read workflow config (project overrides global):
- `.pi/workflows/implement-review-fix-close/config.json`
- `~/.pi/agent/workflows/implement-review-fix-close/config.json`

Key config values:
- `models.implementer` - Model for implementation phase
- `models.review-merge` - Model for review merge
- `models.fixer` - Model for fixes
- `workflow.enableResearcher` - Whether to run research step
- `workflow.knowledgeDir` - Where to store knowledge artifacts

## Execution Procedures

### Procedure: Re-Anchor Context

Run this at the start of EVERY ticket implementation to prevent context rot.

1. **Read root AGENTS.md** (if exists)
   - Check if it references `.pi/ralph/AGENTS.md`
   - If referenced, read `.pi/ralph/AGENTS.md` for lessons learned

2. **Read knowledge base**
   - Check `{knowledgeDir}/tickets/{ticket}.md` for ticket-specific research
   - Read if exists

3. **Get ticket details**
   - Run `tk show {ticket}` to get full ticket description

4. **Parse planning references** (note, don't load yet):
   - "OpenSpec Change: {id}" → `openspec/changes/{id}/`
   - "IRF Seed: {topic}" → `{knowledgeDir}/topics/{topic}/`
   - "Spike: {topic}" → `{knowledgeDir}/topics/{topic}/`
   - Only load if explicitly needed during implementation

### Procedure: Research (Optional)

Skip if: `--no-research` flag OR `workflow.enableResearcher` is false

**With existing research:**
- If `{knowledgeDir}/tickets/{ticket}.md` exists and is sufficient, use it

**Fresh research:**
1. Check available MCP tools (context7, exa, grep_app, zai-web-search)
2. Query each available tool for relevant documentation/code
3. Synthesize findings
4. Write to `{knowledgeDir}/tickets/{ticket}.md`

### Procedure: Implement

1. **Switch to implementer model**:
   ```
   switch_model action="switch" search="{models.implementer}"
   ```

2. **Review all gathered context** from Re-Anchor procedure

3. **Explore codebase**:
   - Use `find` and `grep` to locate relevant files
   - Follow existing patterns from AGENTS.md

4. **Implement changes**:
   - Make focused, single-responsibility changes
   - Track changed files in memory
   - Follow project patterns exactly

5. **Run quality checks**:
   - Load checkers from config
   - Run lint/format on changed files
   - Run typecheck on project
   - Fix any issues found

6. **Run tests**:
   - Execute relevant tests
   - Verify implementation

7. **Write `implementation.md`**:
   ```markdown
   # Implementation: {ticket-id}

   ## Summary
   Brief description of changes

   ## Files Changed
   - `path/to/file.ts` - what changed

   ## Key Decisions
   - Why approach X was chosen

   ## Tests Run
   - Commands and results

   ## Verification
   - How to verify it works
   ```

### Procedure: Parallel Reviews

This is the ONLY step requiring subagents.

**Execute parallel subagents**:
```json
{
  "tasks": [
    {"agent": "reviewer-general", "task": "{ticket}"},
    {"agent": "reviewer-spec-audit", "task": "{ticket}"},
    {"agent": "reviewer-second-opinion", "task": "{ticket}"}
  ]
}
```

Store returned paths for next step.

### Procedure: Merge Reviews

1. **Switch to review-merge model**:
   ```
   switch_model action="switch" search="{models.review-merge}"
   ```

2. **Read all three review outputs**

3. **Deduplicate issues**:
   - Match by file path + line number + description similarity
   - Keep highest severity when duplicates found
   - Note source reviewer(s)

4. **Write consolidated `review.md`**:
   ```markdown
   # Review: {ticket-id}

   ## Critical (must fix)
   - `file.ts:42` - Issue description

   ## Major (should fix)
   - `file.ts:100` - Issue description

   ## Minor (nice to fix)
   - `file.ts:150` - Issue description

   ## Warnings (follow-up ticket)
   - `file.ts:200` - Future work

   ## Suggestions (follow-up ticket)
   - `file.ts:250` - Improvement idea

   ## Summary Statistics
   - Critical: {count}
   - Major: {count}
   - Minor: {count}
   - Warnings: {count}
   - Suggestions: {count}
   ```

### Procedure: Fix Issues

1. **Switch to fixer model** (if different):
   ```
   switch_model action="switch" search="{models.fixer}"
   ```

2. **Check review issues**:
   - If zero Critical/Major/Minor: write "No fixes needed" to `fixes.md`, skip to Close

3. **Fix issues**:
   - Fix all Critical issues (required)
   - Fix all Major issues (should do)
   - Fix Minor issues if low effort
   - Do NOT fix Warnings/Suggestions (these become follow-up tickets)

4. **Re-run tests** after fixes

5. **Write `fixes.md`** documenting what was fixed

### Procedure: Close Ticket

No model switch needed - stay on current model.

1. **Read `implementation.md`, `review.md`, `fixes.md`**

2. **Compose summary note** for ticket

3. **Add note via `tk add-note`**

4. **Close ticket via `tk close`**

5. **Write `close-summary.md`**

### Procedure: Ralph Integration (Optional)

Only if `.pi/ralph/` directory exists:

**Update Progress**:
- Append to `.pi/ralph/progress.md`:
  ```markdown
  - {ticket-id}: {STATUS} ({timestamp})
    - Summary: {one-line}
    - Issues: Critical({c})/Major({m})/Minor({n})
    - Status: COMPLETE|FAILED
  ```

**Extract Lessons** (conditional):
- Only if a gotcha was discovered or pattern emerged
- Append to `.pi/ralph/AGENTS.md`:
  ```markdown
  ## Lesson from {ticket-id} ({date})

  **Context**: {brief context}
  **Lesson**: {what was learned}
  **Apply when**: {when to use this}
  ```

**Output Promise Sigil**:
```
<promise>TICKET_{ticket-id}_{STATUS}</promise>
```

## Full Workflow Execution

### For /irf-lite (Recommended)

```
1. Re-Anchor Context
2. Research (optional)
3. Implement (model-switch)
4. Parallel Reviews (subagents)
5. Merge Reviews (model-switch)
6. Fix Issues (model-switch)
7. Close Ticket
8. Ralph Integration (if active)
```

### For /irf (Original)

Same phases, but steps 3-7 may spawn subagents instead of model-switch.

## Error Handling

- **switch_model fails**: Report error, continue with current model
- **Parallel reviews fail**: Continue with available reviews
- **tk commands fail**: Document in close-summary.md
- **Ralph files fail**: Log warning, don't fail ticket

## Output Artifacts

Always written to current working directory:
- `implementation.md` - What was implemented
- `review.md` - Consolidated review
- `fixes.md` - What was fixed
- `close-summary.md` - Final summary

Ralph files (if active):
- `.pi/ralph/progress.md` - Updated
- `.pi/ralph/AGENTS.md` - May be updated with lessons

Knowledge base (if research ran):
- `{knowledgeDir}/tickets/{ticket}.md`
