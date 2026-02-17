---
description: Create an implementation plan document with optional session attachment [tf-planning +codex-mini]
model: openai-codex/gpt-5.3-codex
thinking: high
skill: tf-planning
---

# /tf-plan

Create a single plan document for a project, feature, or refactor. When a planning session is active, automatically attaches the plan to the session and includes provenance information.

## Usage

```
/tf-plan <request description>
```

## Arguments

- `$@` - The request description for the plan

## Example

```
/tf-plan Refactor auth flow to support OAuth + magic links
```

## Execution

Follow the **TF Planning Skill** "Plan Interview (Planner)" procedure:

### Step 1: Check for Active Session
- Load `.tf/knowledge/.active-planning.json` if it exists
- If `state` is `"active"`, capture `session_id`, `root_seed`, and `spikes` array
- If no active session, proceed with normal flow (no session linking)

### Step 2-5: Create Plan Document
1. Create `plan-*` topic ID
2. Create `.tf/knowledge/topics/{topic-id}/`
3. Write `plan.md` with:
   - Standard sections (Summary, Requirements, Constraints, etc.)
   - **"Inputs / Related Topics" section** (if session active):
     ```markdown
     ## Inputs / Related Topics

     - Root Seed: [{root_seed}](topics/{root_seed}/seed.md)
     - Session: {session_id}
     - Related Spikes:
       - [{spike-1}](topics/{spike-1}/spike.md)
       - [{spike-2}](topics/{spike-2}/spike.md)
     ```
   - Consultant Notes and Reviewer Notes sections
4. Update `index.json`

### Step 6: Attach to Session (if active)
- Update `.active-planning.json`:
  - Set `plan` field to the new plan ID (overwrites any prior plan)
  - Update `updated` timestamp
- Emit notice:
  ```
  [tf] Auto-attached plan to session: {session_id} (root: {root_seed})
  ```

### Step 7: Cross-Link in sources.md (if active session)
- **Root seed `sources.md`**: Add plan link in "Session Links" section (dedup)
- **Plan `sources.md`**: Add "Parent Session" section with root seed link

## Session Behavior

### With Active Session
When a planning session is active (created via `/tf-seed`):
- Plan is automatically attached to the session
- "Inputs / Related Topics" section references the root seed and all recorded spikes
- Cross-links are created in `sources.md` files
- Prior plan for the session (if any) is overwritten

### Without Active Session
When no session is active:
- Plan is created as a standalone document
- No session attachment or cross-linking occurs
- Behavior is identical to the legacy `/tf-plan` command

## Output

**Always created:**
- `plan.md` in `.tf/knowledge/topics/{topic-id}/`
- Status set to `draft`

**When session active:**
- `.active-planning.json` updated with `plan: {topic-id}`
- Cross-links in `{root_seed}/sources.md` and `{topic-id}/sources.md`

## Next Steps

Chained flow (recommended when `pi-prompt-template-model` prompt chaining is available):
```
/tf-plan-chain <request description>
```

Run consultant and reviewer:
```
/tf-plan-consult {topic-id}
/tf-plan-revise {topic-id}
/tf-plan-review {topic-id} --high-accuracy
```

Or proceed directly to backlog generation:
```
/tf-backlog {topic-id}
```
