# spike-pi-non-interactive-logs

Pi’s `-p/--print` (non-interactive) mode normally prints only the final assistant response. To see progress “logs” (tool calls/results, streaming deltas, retries/compaction events) you can run pi in **JSON event stream mode** and format/filter the events (e.g. with `jq`). For fully custom logging, load a small **extension** that subscribes to `tool_call` / `tool_result` and prints to stderr.

## Keywords
- pi
- non-interactive
- logging
- json
- tool events
- extensions
