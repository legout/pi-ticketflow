---
description: Simple Ralph loop using interactive_shell (serial or small parallel batches)
restore: false
model: kimi-coding/k2p5
thinking: medium
---

# /ralph-loop

Run a **simple** Ralph loop in Pi. Process tickets in **serial** by default, or in **small parallel batches** when `--parallel N` is provided. Always return to the main Pi session between batches.

## Usage

```bash
/ralph-loop [--parallel N] [--help]
```

## Flags

| Flag | Default | Meaning |
|---|---:|---|
| `--parallel N` | `1` | Max concurrent tickets per batch |
| `--help` | off | Print usage and exit |

## Preconditions

1. `.tf/ralph/` exists (`tf ralph init`)
2. `.pi/prompts/tf.md` exists (for `/tf`)
3. `pi` and `tk` are in `PATH`

If any precondition fails, stop with a clear error.

## Behavior (Simple Loop)

Repeat until **no ready tickets remain**:

### 1) Find tickets
- Run `tk ready` and select the **first N** tickets where `N = --parallel` (default 1).
- If none, stop.

### 2) Launch sessions (one per ticket)
For each selected ticket, start an `interactive_shell` **dispatch** session:

```bash
pi "/tf <ticket-id> --auto"
```

- Use **one session per ticket**
- Use `mode: "dispatch"`, `background: true`
- Record the returned `sessionId` per ticket

### 3) Monitor and close batch
- Poll each session via `interactive_shell({ sessionId })`
- When a session finishes:
  - record success/failure
  - close it if still running
  - return to the main Pi session
- Wait until **all sessions in the batch finish** before starting the next batch

### 4) Update progress
After each batch, update `.tf/ralph/progress.md` with:
- tickets completed/failed so far
- currently active sessions (if any)
- last updated timestamp

### 5) Lessons learned
After each ticket completes:
- Inspect `.tf/knowledge/tickets/<ticket-id>/`
- If you find clear lessons learned, append to `.tf/ralph/AGENTS.md`
  - include ticket ID + bullet list
- If nothing new, do not modify the file

## Guardrails

- **No lock files, no persistent state**
- **No subprocesses** inside the ticket session
- **No background loop** beyond `interactive_shell` dispatch
- Keep logs concise

## Notes

This is the simple Wiggum-style loop. The stable production runner remains `tf ralph start`.