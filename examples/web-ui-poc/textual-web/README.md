# POC: textual-web for tf UI

## Overview
This POC demonstrates serving the existing Ticketflow TUI using `textual-web`.

## Prerequisites
```bash
pip install textual-web
# or
pipx install textual-web
```

## Running the POC

1. From the repo root directory, run:
```bash
textual-web --config .tf/knowledge/tickets/pt-7t1n/poc/textual-web/serve.toml
```

2. Click the link in the terminal to open in browser

## What You'll See
- The existing Kanban board TUI running in your browser
- Same functionality as terminal: tabs, navigation, ticket viewing
- WebSocket-based terminal emulation via xterm.js

## Observations

### Pros
- ✅ Works immediately with zero code changes
- ✅ All existing TUI features available
- ✅ Fastest proof-of-concept (minutes to demo)
- ✅ Single codebase maintained

### Cons
- ❌ Terminal-like UX in browser (not native web feel)
- ❌ No URL routing (can't link to specific ticket)
- ❌ Requires JavaScript/WebSocket
- ❌ Mobile experience is limited
- ❌ No graceful degradation without JS

## Verdict
Best for: Quick win, internal tools, terminal-first teams
Not ideal for: Public-facing, mobile-heavy, accessibility-critical use cases
