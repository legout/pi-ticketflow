---
description: Native dispatch-mode Ralph loop (experimental)
restore: false
model: kimi-coding/k2p5
thinking: medium
---

# /ralph-loop

Run an autonomous Ralph loop in Pi using `interactive_shell` dispatch sessions.

This is an **experimental** orchestrator. The stable production runner remains `tf ralph start`.

## Usage

```bash
/ralph-loop [--max-iterations N] [--parallel N] [--dry-run] [--help]
```

## Flags

| Flag | Default | Meaning |
|---|---:|---|
| `--max-iterations N` | `50` | Maximum number of tickets to start in this run |
| `--parallel N` | `1` | Maximum concurrent dispatch sessions |
| `--dry-run` | off | Plan/log only; do not launch sessions or mutate persistent state |
| `--help` | off | Print usage/flags and exit without state changes |

## Preconditions

1. `.tf/ralph/` exists (`tf ralph init`)
2. `prompts/tf.md` exists
3. `pi` and `tk` are in `PATH`

If any precondition fails, stop with a clear error.

## Concurrency Lock

Use lock file:

```
.tf/ralph/dispatch-loop.lock
```

- Lock content must include `runId`, `pid`, and `startedAt`.
- Locking applies to normal mode only (`--dry-run` skips lock/state changes).
- At turn start, read state first to discover the current `runId` (or create one for a new run), then reconcile lock:
  - if lock is missing, create it for this `runId`;
  - if lock exists for the same `runId`, continue (re-entrant turn);
  - if lock exists for a different `runId` and owner process is alive, stop and report another loop is active;
  - if lock exists for a different `runId` and owner process is dead, treat as stale lock, log cleanup, and replace it.
- Keep lock handling idempotent across turns.
- Release lock when the run reaches a terminal state (completion/failure) and state file is finalized.

## State File

Persist state in:

```
.tf/ralph/dispatch-loop-state.json
```

Schema:

```json
{
  "version": 1,
  "runId": "uuid",
  "startedAt": "ISO8601",
  "maxIterations": 50,
  "parallel": 1,
  "startedCount": 0,
  "completed": [],
  "failed": [],
  "active": {
    "<sessionId>": {
      "ticket": "pt-xxxx",
      "startedAt": "ISO8601"
    }
  }
}
```

Write atomically (temp file + rename).

## Execution Contract

### 1) Parse arguments

- Parse `$ARGUMENTS` for supported flags only.
- If `--help` is present, print usage/flags and exit immediately.
- Reject unknown flags.
- Validate `--max-iterations >= 1`, `--parallel >= 1`.

### 2) Load or initialize state

- If `--dry-run` is set, run stateless:
  - do not create/modify lock file,
  - do not create/modify state file,
  - do not modify `.tf/ralph/progress.md`,
  - initialize local in-memory planning state (for example `plannedCount = 0`, `plannedTickets = set()`, `active = {}`).
- Otherwise:
  - if state file exists, resume it;
  - else initialize a new state from flags;
  - if state is unreadable/invalid JSON:
    - move it to `.tf/ralph/dispatch-loop-state.corrupt.<timestamp>.json`,
    - initialize fresh state,
    - log the recovery action;
  - if state exists and incoming flags disagree with persisted `maxIterations`/`parallel`, keep persisted values for this run and log the mismatch.

### 3) Reconcile active sessions

- In `--dry-run`, skip this step (no active sessions are launched).
- In normal mode, for each `sessionId` in `active`:
  - If current turn includes dispatch completion for this session, use it.
  - If no completion payload is available (e.g., resumed run), query status via `interactive_shell({ sessionId })`.
  - If session finished successfully: move ticket to `completed`.
  - If session failed/killed/exited non-zero: move ticket to `failed`.
  - Remove finished sessions from `active`.

### 4) Fill capacity

While both are true:
- normal mode: `startedCount < maxIterations`
- dry-run mode: `plannedCount < maxIterations`
- `len(active) < parallel`

Do:
1. Compute `remaining_capacity = parallel - len(active)`.
2. Fetch up to `remaining_capacity` tickets in one call, for example:
   ```bash
   tk ready | awk '{print $1}' | head -n "$remaining_capacity"
   ```
3. Remove empties and duplicates.
4. Exclude tickets already present in `active`.
5. Exclude tickets already marked `completed` in this run.
6. In `--dry-run`, also exclude tickets already in `plannedTickets`.
7. If `parallel > 1`, enforce conservative component safety before launch:
   - for each candidate ticket, read `component:*` tags via `tk show <ticket>`;
   - skip tickets whose components overlap with currently active tickets in this run.
8. If none remain: break.
9. For each selected ticket:
   - If `--dry-run`: log planned dispatch, increment `plannedCount`, add ticket to `plannedTickets`, and continue.
   - Launch dispatch via `interactive_shell`:
     - `command: 'pi "/tf <ticket-id> --auto"'`
     - `mode: "dispatch"`
     - `background: true`
   - If launch fails or no `sessionId` is returned:
     - append ticket to `failed` with a short reason,
     - increment `startedCount`,
     - continue to next ticket.
   - Otherwise record returned `sessionId` in `active`.
   - Increment `startedCount`.
   - Log attach hint: `pi /attach <sessionId>`.

### 5) Progress + completion

- In normal mode, update `.tf/ralph/progress.md` with:
  - started/completed/failed counters
  - active session count
  - latest outcomes (if any)
- In `--dry-run`, print a concise plan summary and exit without writing files.

Completion rules (normal mode):
- If there are no ready tickets **and** `active` is empty, emit:
  ```text
  <promise>COMPLETE</promise>
  ```
  then remove state file and stop.
- If `startedCount >= maxIterations` and `active` is empty, emit:
  ```text
  <promise>COMPLETE</promise>
  ```
  then remove state file and stop.

In normal mode, if neither completion rule is met, persist state and return. The next dispatch completion trigger should continue the run.

## Guardrails

1. Do **not** run `/tf` directly via `bash`; only use `interactive_shell` dispatch.
2. Never launch the same ticket twice in one run while it is active or already marked completed.
3. Keep logs concise and actionable.
4. Never silently drop state; if state is corrupt, back it up and reinitialize.
5. If unsure in parallel mode, launch fewer tickets.

## Notes

- Native dispatch orchestration is useful for experimentation and live observability.
- `tf ralph start` remains the recommended stable path.
