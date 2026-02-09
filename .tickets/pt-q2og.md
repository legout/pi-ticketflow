---
id: pt-q2og
status: closed
deps: [pt-gnhr]
links: [pt-2xr4]
created: 2026-02-09T13:42:03Z
type: task
priority: 2
assignee: legout
external-ref: spike-modern-simple-css-dashboard-kanban
tags: [tf, backlog, component:docs, component:tests]
---
# Accessibility pass for web UI styling (focus-visible, contrast, reduced motion)

## Task
Ensure the web UI has clear focus states, sufficient contrast for key UI elements, and respects reduced motion preferences.

## Context
Dashboards are keyboard-heavy. Modern minimal CSS can inadvertently reduce contrast or remove focus outlines; we should harden basics.

## Acceptance Criteria
- [ ] `:focus-visible` produces a clear outline across interactive elements (buttons/links/cards).
- [ ] Priority/status badges have readable contrast in light mode (and dark mode if enabled).
- [ ] Animations/transitions are disabled or reduced when `prefers-reduced-motion: reduce`.

## Constraints
- Keep changes minimal and testable (manual keyboard navigation is fine).

## References
- Spike: spike-modern-simple-css-dashboard-kanban



## Notes

**2026-02-09T14:33:00Z**

Accessibility improvements implemented:

- Added :focus-visible styles for all interactive elements (links, buttons, inputs, ticket cards)
- Updated priority badge colors for WCAG AA compliance (4.5:1+ contrast)
- Added prefers-reduced-motion media query support

Commit: ca64cb4
