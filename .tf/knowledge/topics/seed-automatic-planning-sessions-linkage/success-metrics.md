# Success Metrics: seed-automatic-planning-sessions-linkage

## Primary Metrics
- Users can run a seed→spike→plan→backlog flow without manually editing `sources.md` to keep artifacts linked.
- Reduced “lost context” incidents (subjective): fewer questions like “which spike was for this plan?”
- Lower friction: the default flow feels natural (seed activates session automatically).

## Proxy / Measurable Signals
- Session state file exists and is updated correctly during planning commands.
- Archived snapshots exist for previous sessions after switching.
- Backlog completion reliably finalizes and deactivates the session (no accidental linking afterwards).

## Guardrails
- Backwards compatibility: `--no-session` preserves old behavior.
- No data loss: archived snapshots keep enough info to resume and to audit what happened.
