---
description: Run full plan lifecycle with prompt chaining (plan -> consult -> revise -> review) [tf-planning +codex-mini]
model: openai-codex/gpt-5.3-codex
thinking: high
skill: tf-planning
---

# /tf-plan-chain

Run the full plan lifecycle in one command, using `pi-prompt-template-model` prompt chaining.

## Usage

```
/tf-plan-chain <request description>
```

## Arguments

- `$@` - Request description used to create the initial plan

## Execution

1. Prefer chained execution via:
   - `/chain-prompts tf-plan "$@" -> tf-plan-consult -> tf-plan-revise -> tf-plan-review -- --high-accuracy`
2. If `/chain-prompts` is unavailable, run the same four commands sequentially.
3. Report:
   - final plan ID/path
   - final plan status (`approved` or `blocked`)
   - key blocked reasons (if any)

## Output

- Updated `plan.md` in `.tf/knowledge/topics/plan-*/`
- Status transitions: `draft -> consulted -> revised -> approved|blocked`
