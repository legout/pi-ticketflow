# Sources

## Parent Session

- Root Seed: [seed-add-ralph-loop-background-interactive](../seed-add-ralph-loop-background-interactive/seed.md)
- Session: seed-add-ralph-loop-background-interactive@2026-02-13T15-28-56Z
- Related Spikes:
  - [spike-interactive-shell-execution](../spike-interactive-shell-execution/spike.md)

## Code References

- `tf/ralph.py` - Ralph implementation, especially `run_ticket()` and `build_cmd()`
- Interactive shell skill - `/home/volker/.pi/agent/skills/interactive-shell/SKILL.md`

## User Discussion

- 2026-02-13: Proposal to run Ralph ticket implementations via background `interactive_shell` sessions using `pi /tf ... --auto`, with optional live watching/attachment and parallel execution.
