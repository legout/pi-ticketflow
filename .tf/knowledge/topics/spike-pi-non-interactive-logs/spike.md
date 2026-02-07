# Spike: Show logs/progress in Pi non-interactive mode

## Summary
When you run Pi in non-interactive mode (`pi -p ...`), the default **text** output is intentionally minimal (final assistant response only). `--verbose` affects startup output, but it’s not a full “progress log”. If you want “logs” (tool execution boundaries, partial streaming output, retries/compaction notifications), the built-in way is to run Pi in **JSON event stream mode** (`pi --mode json ...`) and format the JSONL stream into the log lines you want.

If you need human-friendly logs *without* JSON parsing, the extensible way is to load a small **extension** that subscribes to lifecycle/tool events (`tool_call`, `tool_result`, `turn_start`, etc.) and prints to stderr.

## Key Findings
1. **`--mode json` streams all events as JSON lines**, including tool execution start/end, message streaming deltas, auto-retry, and compaction events. This is the most reliable way to observe progress headlessly. (See `docs/json.md`.)
2. **`-p/--print` is “final answer only” by design** in text mode; it’s not intended to be verbose. Use JSON mode (or an extension) if you need progress visibility. (See README / `pi --help`.)
3. **Extensions can log anything you need**: Pi exposes event hooks like `tool_call` and `tool_result` which you can use to print structured lines to stderr while keeping stdout for the main response. (See `docs/extensions.md`.)

## Options Considered

### Option A (recommended): JSON event stream + `jq` formatting
Run Pi in JSON mode and filter the stream in real time.

Examples:

**1) Show tool calls (start/end):**
```bash
pi --mode json -p "Summarize the repo" \
| jq -r --unbuffered '
  if .type=="tool_execution_start" then
    "[tool:start] \(.toolName) \(.args|tostring)"
  elif .type=="tool_execution_end" then
    "[tool:end]   \(.toolName) error=\(.isError)"
  else empty end
'
```

**2) Stream assistant text (like a live log):**
```bash
pi --mode json -p "Explain what you are doing" \
| jq -r --unbuffered '
  select(.type=="message_update")
  | select(.assistantMessageEvent.type=="text_delta")
  | .assistantMessageEvent.delta
'
```

**3) Capture a JSONL trace file while also printing formatted logs:**
```bash
pi --mode json -p "Do X" \
| tee run.jsonl \
| jq -r --unbuffered 'select(.type=="tool_execution_start" or .type=="tool_execution_end")'
```

Pros:
- Zero code changes, uses Pi built-ins.
- Maximum observability (you can choose exactly which events to show).

Cons:
- Output is JSONL; you typically need a formatter (jq/script).

### Option B: Write an extension that logs events (stderr)
Create a small TypeScript extension that subscribes to events and prints logs.

Sketch (not complete):
```ts
export default function (pi) {
  pi.on("tool_call", (e) => {
    process.stderr.write(`[tool_call] ${e.toolName} ${JSON.stringify(e.input)}\n`);
  });
  pi.on("tool_result", (e) => {
    process.stderr.write(`[tool_result] ${e.toolName} isError=${e.isError}\n`);
  });
}
```
Then run:
```bash
pi -e ./my-logger-extension.ts -p "Do X"
```

Pros:
- Human-friendly logs without JSON parsing.
- You decide formatting, redaction, and verbosity flags.

Cons:
- You have to maintain the extension.

### Option C: Use RPC mode (`--mode rpc`) with a custom client
If you’re integrating Pi into another program, RPC mode is the right foundation: your client can receive events/messages and present logs however you like.

Pros:
- Best for long-running integrations.

Cons:
- More work than JSON mode.

## Recommendation
For “show me what’s happening” in non-interactive runs, use **`--mode json`** and format the stream with `jq --unbuffered`.

If you need the logs to be *plain text* and/or to go to **stderr** while keeping stdout clean for pipelines, implement a small **logger extension** using `tool_call`/`tool_result` hooks.

## Risks & Unknowns
- **Noise / secrets**: logging tool inputs/results can leak file contents or API keys. Prefer logging tool names + paths, and redact sensitive args.
- **Buffering**: some pipelines buffer output; use `jq --unbuffered` and/or `stdbuf -oL` if needed.

## Next Steps
- Decide what you want to see as “logs”: tool boundaries only, or full streaming deltas.
- If JSON mode is sufficient: standardize a `jq` filter snippet for your workflow.
- If you need richer logs: create a small `pi` extension and load it in headless runs (`-e`).
