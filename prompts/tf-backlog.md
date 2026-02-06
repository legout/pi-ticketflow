---
description: Create tickets from seed, baseline, or plan artifacts [tf-planning +codex-mini]
model: openai-codex/gpt-5.1-codex-mini
thinking: medium
skill: tf-planning
---

# /tf-backlog

Generate small, actionable implementation tickets from seed (greenfield), baseline (brownfield), or plan artifacts.

## Usage

```
/tf-backlog <seed-baseline-or-plan-path-or-topic-id> [--no-deps] [--no-component-tags] [--no-links] [--links-only]
```

## Arguments

- `$1` - Path to seed/baseline/plan directory or topic ID (`seed-*`, `baseline-*`, or `plan-*`)
- If omitted: auto-locates if exactly one seed, baseline, or plan exists

## Options

- `--no-deps` - Skip automatic dependency inference for seed/baseline backlogs
- `--no-component-tags` - Skip automatic component tag assignment during ticket creation
- `--no-links` - Skip automatic linking of related tickets
- `--links-only` - Run only linking on existing backlog tickets (no new tickets created). Useful for retroactive linking of existing backlogs.

## Examples

```
/tf-backlog seed-build-a-cli
/tf-backlog baseline-myapp
/tf-backlog plan-auth-rewrite
/tf-backlog .tf/knowledge/topics/baseline-myapp/
/tf-backlog seed-build-a-cli --no-component-tags
/tf-backlog seed-myfeature --no-links
/tf-backlog baseline-myapp --no-deps --no-component-tags --no-links
```

### Hint-Based Override Example

When seed content contains ordering keywords, tickets are reordered accordingly:

```
# Seed contains: "Setup project", "Implement auth", "Test endpoints"
/tf-backlog seed-myapi
# Creates tickets in order: Setup → Implement → Test (not creation order)
```

Keywords detected: `setup`/`configure` (first), `define`/`design` (before implement), `implement` (before test), `test` (last).

### --no-deps Example

Create backlog without automatic dependency chaining:

```
/tf-backlog seed-standalone-tasks --no-deps
```

Useful when tasks are truly independent and can be worked on in any order.

### --links-only Example

Run linking on existing backlog without creating new tickets:

```
/tf-backlog seed-myfeature --links-only
```

Useful when:
- A backlog was created before the linking feature existed
- You want to retroactively link related tickets in an existing backlog
- Tickets were created manually but you want automatic linking applied

## Execution

Follow the **TF Planning Skill** "Backlog Generation (Seed, Baseline, or Plan)" procedure:

**Special case: `--links-only` mode**
- If `--links-only` is provided: Skip ticket creation (steps 5-7), go directly to linking step
- Load existing tickets from `backlog.md` instead of creating new ones
- Apply linking criteria to existing tickets
- Update `backlog.md` with links column

**Session Handling:**
- At start: Check for `.active-planning.json`. If exists and `state: active`, capture `session_id` and `root_seed` for later finalization. Skip session finalization if state is not `active`.
- Track ticket creation success/failure during steps 5-7 for error handling.
- At end (if session was active): Record backlog metadata, write archived snapshot, deactivate session.

1. Locate topic directory
2. Detect mode (seed vs baseline vs plan)
3. Read relevant artifacts and plan status (warn if plan not approved)
4. Load existing tickets to avoid duplicates (or to link, if `--links-only`):
   - Read `backlog.md` if it exists
   - Read `existing-tickets.md` if present (from `/tf-baseline`)
   - Run `tk list --help` (or `tk help`) to discover listing/search options
   - If `tk` supports listing/search, pull open tickets with tags like `tf`, `baseline`, or `backlog`
5. Create the appropriate number of small tickets (1-2 hours each, 30 lines max) to cover the scope—this could be 1 ticket for a tiny fix or many for a large refactor. Skip duplicates (record skipped items in backlog.md). **Skip this step if `--links-only` provided.**
6. Create via `tk create` (skip if `--links-only` provided):

   **Seed:**

   ```bash
   tk create "<title>" \
     --description "<description>" \
     --tags tf,backlog,<component-tags> \
     --type task \
     --priority 2 \
     --external-ref "{topic-id}"
   ```

   **Baseline:**

   ```bash
   tk create "<title>" \
     --description "<description>" \
     --tags tf,backlog,baseline,<component-tags> \
     --type task \
     --priority 2 \
     --external-ref "{topic-id}"
   ```

   **Plan:**

   ```bash
   tk create "<title>" \
     --description "<description>" \
     --tags tf,backlog,plan,<component-tags> \
     --type task \
     --priority 2 \
     --external-ref "{topic-id}"
   ```

7. Infer dependencies (skip if `--links-only` provided):

   **Plan mode:**
   - Use Work Plan phases or ordered steps to determine sequencing
   - For phase-based plans: each ticket in phase N depends on all tickets in phase N-1
   - For ordered lists without phases: chain each ticket to the previous one
   - Apply with `tk dep <id> <dep-id>`

   **Seed mode (if `--no-deps` NOT provided):**
   - **Default chain**: Create a simple linear dependency chain in ticket creation order
   - Each ticket N depends on ticket N-1 (the previous one created)
   - Apply with `tk dep <id> <dep-id>`
   - **Out-of-order creation**: The chain reflects creation sequence, not ticket ID order. If you create ticket 5 before ticket 3, ticket 5 becomes the chain head and ticket 3 depends on it. To fix: `tk dep <ticket-3> <ticket-5>` then `tk dep <ticket-5> --remove`.
   - **Hint-based override**: If seed content suggests a different order (e.g., keywords like "define", "implement", "test", "setup", "configure"), adjust the chain to match the logical sequence:
     - "Setup" or "Configure" tasks come first
     - "Define" or "Design" tasks come before "Implement"
     - "Implement" tasks come before "Test"
   - Conservative: prefer the default chain over uncertain deps; skip deps if the order is ambiguous

   **Baseline mode:**
   - Skip dependencies unless explicitly stated in source docs
   - Apply with `tk dep <id> <dep-id>`

8. **Apply component tags by default** (skip if `--no-component-tags` or `--links-only` provided):
   - For each ticket, analyze title and description using the shared component classifier
   - Import and use `tf_cli.component_classifier.classify_components()` - the same
     module used by `/tf-tags-suggest` to ensure consistent suggestions:
     ```python
     from tf_cli.component_classifier import classify_components, format_tags_for_tk
     
     result = classify_components(title, description)
     component_tags = result.tags  # e.g., ['component:cli', 'component:tests']
     ```
   - Apply component tags to tickets during creation via `--tags`:
     ```bash
     tk create "<title>" \
       --description "<description>" \
       --tags "tf,backlog,component:cli" \
       ...
     ```
   - Only assign tags when the classifier returns confident matches
   - Tickets without confident component matches are left untagged (no random tagging)
   - If skipped, users can re-run tagging later via `/tf-tags-suggest --apply`

9. Link related tickets (if `--no-links` NOT provided):
   - **If `--links-only`**: Load existing tickets from `backlog.md`, apply linking to those
   - **Otherwise**: Link newly created tickets that are tightly related for discoverability
   - **Criteria** (conservative - under-linking preferred):
     - Same component tags + adjacent in creation order
     - Title similarity (significant shared words)
   - Apply with `tk link <id1> <id2>` (symmetric links)
   - Max 2-3 links per ticket to avoid noise

10. Write `backlog.md` with ticket summary (include dependencies, component tags, and links)

11. **Session Finalization** (if an active session was found at start):
    - Ensure `sessions/` directory exists: `mkdir -p .tf/knowledge/sessions`
    - Read `.active-planning.json` to get current session state
    - Verify session is still `state: active` (skip if changed)
    - Build session data:
      - Set `backlog.topic` to the topic-id
      - Set `backlog.backlog_md` to `topics/{topic-id}/backlog.md`
      - Set `backlog.tickets` to array of created ticket IDs (may be empty if all skipped)
      - Update `updated` timestamp to now
    - **If all tickets created successfully** (or zero tickets due to all duplicates):
      - Write archived session snapshot to `sessions/{session_id}.json`:
        ```json
        {
          "schema_version": 1,
          "session_id": "{session_id}",
          "state": "archived",
          "root_seed": "{root_seed}",
          "spikes": [...],
          "plan": "...",
          "backlog": {
            "topic": "{topic-id}",
            "backlog_md": "topics/{topic-id}/backlog.md",
            "tickets": ["id1", "id2", ...]
          },
          "created": "...",
          "updated": "{ISO8601 timestamp}",
          "completed_at": "{ISO8601 timestamp}"
        }
        ```
      - Remove `.active-planning.json` to deactivate the session
      - Emit notice: `[tf] Session archived: {session_id} ({count} tickets created)`
    - **If ticket creation failed part-way** (any `tk create` returned error):
      - Write error session snapshot to `sessions/{session_id}.json`:
        ```json
        {
          "schema_version": 1,
          "session_id": "{session_id}",
          "state": "error",
          "root_seed": "{root_seed}",
          "spikes": [...],
          "plan": "...",
          "backlog": {
            "topic": "{topic-id}",
            "backlog_md": "topics/{topic-id}/backlog.md",
            "tickets": ["id1", ...]
          },
          "error": {
            "message": "Ticket creation failed during backlog generation",
            "failed_at": "step-{N}",
            "tickets_created": ["id1", ...],
            "timestamp": "{ISO8601 timestamp}"
          },
          "created": "...",
          "updated": "{ISO8601 timestamp}",
          "completed_at": null
        }
        ```
      - **Do NOT remove** `.active-planning.json` (leave active for retry)
      - Emit notice: `[tf] Session error: {session_id} (ticket creation failed, {count} tickets created before error)`

## Ticket Templates

**Seed**

```markdown
## Task

<Single-sentence description>

## Context

<2-3 sentences from seed>

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Constraints

<Relevant constraints>

## References

- Seed: <topic-id>
```

**Baseline**

```markdown
## Task

<Single-sentence description>

## Context

<2-3 sentences from baseline/risk/test inventory>

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Constraints

<Relevant constraints>

## References

- Baseline: <topic-id>
- Source: risk-map.md|test-inventory.md|dependency-map.md
```

**Plan**

```markdown
## Task

<Single-sentence description>

## Context

<2-3 sentences from plan summary/requirements>

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Constraints

<Relevant constraints>

## References

- Plan: <topic-id>
```

## Output

**Normal mode:**
- Tickets created in `tk` (with external-ref linking to source)
- Dependencies applied via `tk dep` when inferred
- Related tickets linked via `tk link` when applicable
- `backlog.md` written to topic directory
- **Session finalization** (if session was active): Session snapshot written to `sessions/{session_id}.json` with `state: archived` (or `state: error` on failure), `.active-planning.json` removed on success

**`--links-only` mode:**
- No new tickets created
- Existing tickets from `backlog.md` linked via `tk link` when applicable
- `backlog.md` updated with Links column
- **No session finalization** (session remains active for full backlog generation)

## Next Steps

The planning session is now complete. Start implementation:

```
/tf <ticket-id>
```

To begin a new planning session, run `/tf-seed <idea>`.
