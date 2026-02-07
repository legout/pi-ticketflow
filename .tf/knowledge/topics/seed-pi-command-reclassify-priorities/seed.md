# Seed: Add a Pi command to reclassify ticket priorities (P0–P4)

## Vision
Backlog triage is often inconsistent because priority meanings drift over time. Provide a single command that applies a clear rubric so tickets are classified consistently and quickly.

## Core Concept
Introduce a new Pi command (e.g. `/tf-reclassify-priority` or similar) that reviews one or more tickets and proposes/sets `priority` according to a rubric:
- **P0–P1**: critical bug/risk (security, data correctness, OOM)
- **P2**: real product features
- **P3**: important engineering quality / dev workflow
- **P4**: code cosmetics / refactors / docs / test typing polish

The command should support a **dry-run** mode (show proposed changes) and an **apply** mode (update tickets).

## Key Features
1. **Rubric-driven mapping**: encode the P0–P4 rubric as the canonical source.
2. **Bulk operation**: allow running on a list (e.g. “ready” tickets) or on explicit IDs.
3. **Safe updates**: default to dry-run; only update with an explicit `--apply` flag.
4. **Explainability**: for each ticket, print the matched rubric category and a short reason.
5. **Audit trail (optional)**: write a small report into `.tf/knowledge/` (or a session artifact) so reclassifications are reviewable.

## Open Questions
- What is the exact Ticketflow `priority` scale (numeric mapping) and does it match P0–P4 directly?
- What `tk` commands exist for updating a ticket’s priority (and does it support bulk updates)?
- Should the rubric be configurable (settings file), or hard-coded initially?
- Which ticket fields should be used for classification (tags, title keywords, description patterns)?
- Should closed/archived tickets be excluded by default?
