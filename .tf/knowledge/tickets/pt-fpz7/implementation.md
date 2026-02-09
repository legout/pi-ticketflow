# Implementation: pt-fpz7

## Summary
Added `tf ui --web` helper that prints the recommended `textual serve` invocation instead of launching a web server directly.

## Changes Made

### tf_cli/ui.py
Modified the `--web` flag behavior in the `main()` function:

- **Before**: `--web` launched a Sanic web server via `run_web_server()`
- **After**: `--web` prints a copy-pasteable `textual serve` command with security warnings

The command format is:
```
textual serve "tf ui" --host {host} --port {port}
```

Default values:
- `--host`: 127.0.0.1 (localhost only)
- `--port`: 8000

## Security Warnings Included
The output includes warnings about:
1. Default localhost-only binding
2. Risks of using `--host 0.0.0.0` (public network exposure)
3. No authentication provided

## Acceptance Criteria Verification
- [x] `tf ui --web` prints a copy/paste `textual serve "tf ui"` command
- [x] Includes warning text about localhost default and public binding risks
- [x] No config parsing, auth, or process management added
- [x] Implementation is minimal and focused

## Test Run
```bash
$ python -m tf_cli ui --web

🌐 To serve the Ticketflow UI in a web browser, run:

   textual serve "tf ui" --host 127.0.0.1 --port 8000

⚠️  WARNING: Security considerations for web serving:
   • The default host (127.0.0.1) only allows local access
   • Use --host 0.0.0.0 to bind to all interfaces (allows external access)
   • Binding to 0.0.0.0 exposes the UI on your network - ensure proper firewall rules
   • No authentication is provided - anyone with access can view tickets
```

## Files Changed
- `tf_cli/ui.py` - Modified `--web` flag behavior in `main()` function
