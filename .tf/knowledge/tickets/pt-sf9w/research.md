# Research: pt-sf9w

## Task
Verify Ticketflow UI runs via `textual serve` for both installed and dev workflows.

## Context
- UI is in `tf_cli/ui.py` with `main()` entry point
- `tf ui` command launches the TUI via `cli.py`
- Dependencies: `textual>=7.5.0`, `textual-dev>=1.8.0`, `textual-web>=0.4.2`

## Textual Serve Basics
Textual's dev tools provide `textual serve` command for serving Textual apps in a browser.
Syntax options:
- `textual serve "module.path:AppClass"` - serve a textual app
- For CLI commands, use `--command` flag or wrap in shell

## Approaches to Test

### 1. Installed workflow: `textual serve "tf ui"`
May need: `textual serve --command "tf ui"`

### 2. Dev workflow: `textual serve "python -m tf_cli.ui"`
Requires module to be directly runnable (has `if __name__ == "__main__"` pattern)
Current `tf_cli/ui.py` only has `main()` function, needs a `run()` call.

## Verification Steps
1. Check textual serve is available: `textual --help`
2. Test installed command
3. Test dev module command  
4. Document URL/port defaults and any quirks
