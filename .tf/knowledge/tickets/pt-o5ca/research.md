# Research: pt-o5ca

## Status
Research completed. No additional external research required - this is a design decision ticket based on existing knowledge of the `/chain-prompts` feature.

## Rationale
This ticket requires understanding the `/chain-prompts` feature from `pi-prompt-template-model` and mapping existing TF workflow flags to a chain-based architecture. The research was conducted through:

1. **Spike document review** - `spike-chain-prompts-prompt-template` provides detailed analysis of `/chain-prompts` capabilities and limitations
2. **Plan review** - `plan-replace-pi-model-switch-extension` outlines the migration strategy
3. **Current workflow analysis** - Understanding existing flags and their purposes

## Context Reviewed

### `/chain-prompts` Key Properties
- Sequential execution with no branching/conditionals
- Each step has its own model/skill/thinking from frontmatter
- Context flows via conversation history (not explicit file passing)
- Original model/thinking restored at chain end (or on failure)

### Existing TF Flags
| Flag | Purpose | Challenge with `/chain-prompts` |
|------|---------|--------------------------------|
| `--no-research` | Skip research phase | Chain has no skip/conditional logic |
| `--with-research` | Force research even if disabled | Same as above |
| `--create-followups` | Run follow-up creation after review | Post-chain step |
| `--final-review-loop` | Run review loop after close | Post-chain step |
| `--simplify-tickets` | Simplify tickets after implementation | Post-chain step |

### Options Considered

**Option 1: Multiple chain variants**
- `/tf` - full chain with research
- `/tf-no-research` - chain starting at implement
- Pros: Simple, explicit
- Cons: Combinatorial explosion with more flags

**Option 2: Conditional logic inside prompts**
- Each phase prompt checks flags and decides to noop
- Pros: Single entry point
- Cons: Violates chain-prompts philosophy (steps still execute, just do nothing)

**Option 3: Hybrid approach (SELECTED)**
- Research control: Entry point variants (`/tf-research` vs `/tf-implement`)
- Post-chain steps: Separate commands after chain completes
- Pros: Clean separation, backward compatible, no combinatorial explosion

## Sources
- `.tf/knowledge/topics/spike-chain-prompts-prompt-template/spike.md`
- `.tf/knowledge/topics/plan-replace-pi-model-switch-extension/plan.md`
- `.tf/config/settings.json` (workflow configuration)
