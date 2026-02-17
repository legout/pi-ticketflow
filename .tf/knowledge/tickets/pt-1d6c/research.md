# Research: pt-1d6c

## Status
Research completed

## Rationale
- Research was conducted to gather context for implementation
- Internal knowledge base and referenced documents were reviewed

## Context Reviewed
- `tk show pt-1d6c`
- Spike: topics/Switch/

## Ticket Summary

# Implement kanban board view in web UI (Datastar)

## Task
Implement the kanban board view displaying tickets in Ready/Blocked/In Progress/Closed columns using **Datastar**.

## Context
The kanban board is the primary view of the tf ui. In web mode, this should display tickets in their respective columns with basic ticket information. Uses **Datastar** for reactivity and server interactions.

## Acceptance Criteria
- [ ] Display four columns: Ready, Blocked, In Progress, Closed
- [ ] Load tickets using existing TicketLoader and BoardClassifier
- [ ] Display ticket cards with ID, title, and priority
- [ ] Color-code or label tickets by priority (P0-P4)
- [ ] Click ticket card to open detail view (using `data-on:click="@get('/ticket/{id}')"`)
- [ ] Manual refresh button using `data-on:click="@get('/api/refresh')"`
- [ ] Handle empty states (no tickets in a column)
- [ ] Use Datastar's `data-signals` for any client-side state if needed

## Datastar-Specific Implementation Notes
- Include Datastar CDN in base template: `https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.7/bundles/datastar.js`
- Use colon-delimited attributes: `data-on:click` (not `data-on-click`)
- Backend endpoints return HTML fragments; Datastar morphs them into DOM
- For partial board refresh, return only the board HTML fragment

## Example Template Pattern
```html
<div id="board">
  <div class="column" id="col-ready">
    {%- for ticket in columns.ready %}
    <div class="ticket-card" id="ticket-{{ ticket.id }}"
         data-on:click="@get('/ticket/{{ ticket.id }}')">
      <span class="priority p{{ ticket.priority }}">P{{ ticket.priority }}</span>
      <span class="ticket-id">{{ ticket.id }}</span>
      <span class="title">{{ ticket.title }}</span>
    </div>
    {%- endfor %}
  </div>
  <!-- similar for blocked, in_progress, closed -->
</div>
<button data-on:click="@get('/api/refresh')">Refresh</button>
```

## Constraints
- Reuse existing ticket loading and classification logic
- P

## Sources
- Ticket database (`tk show`)
- Project knowledge base
- Knowledge base topics (seeds/spikes)