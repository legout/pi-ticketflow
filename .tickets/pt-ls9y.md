---
id: pt-ls9y
status: closed
deps: [pt-sf9w]
links: [pt-sf9w, pt-uo1b]
created: 2026-02-09T11:48:25Z
type: task
priority: 2
assignee: legout
external-ref: plan-allow-to-serve-the-textual-app-as-a-web
tags: [tf, backlog, plan, component:cli, component:docs, component:workflow]
---
# Document web mode: `textual serve` for `tf ui`

## Task
Add a “Web mode” section to user-facing docs describing how to run the TUI in a browser via `textual serve`.

## Context
We want a safe-by-default, copy/paste workflow for local browser access, with clear warnings for non-local binding.

## Acceptance Criteria
- [ ] Docs include prerequisites (`textual-dev` provides the `textual` CLI)
- [ ] Docs include both commands: `textual serve "tf ui"` and dev fallback `textual serve "python -m tf_cli.ui"`
- [ ] Docs mention `textual serve --help` for host/port flags and warn against public binding
- [ ] Docs state lifecycle behavior (what happens when the browser tab closes)

## Constraints
- Keep `textual-web` explicitly out-of-scope unless marked experimental

## References
- Plan: plan-allow-to-serve-the-textual-app-as-a-web


## Notes

**2026-02-09T14:10:30Z**

**Implementation Complete**

Added comprehensive Web Mode documentation to README.md documenting how to run the Ticketflow TUI in a browser via textual serve.

**Changes:**
- Added 'Web Mode (Browser UI)' section to README.md with:
  - Prerequisites (textual-dev package)
  - Both command variants (installed CLI and dev fallback)
  - Access instructions (default http://localhost:8000)
  - Host/port customization via textual serve flags
  - Prominent security warning for public binding
  - Session lifecycle documentation

**Review:**
- Critical: 0, Major: 0, Minor: 0
- All acceptance criteria met

**Commit:** c62fe2edb2ba2536697c89be0f54ab2fc1b124d9
