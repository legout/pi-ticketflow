# MVP Scope

## In Scope

- Create phase prompts (`tf-research`, `tf-implement`, `tf-review`, `tf-fix`, `tf-close`) that each run their phase end-to-end.
- Create a chained entry point (`/tf` or new `/tf-irf`) that uses `/chain-prompts` to run all phases sequentially.
- Remove dependency on `pi-model-switch` for the chained workflow.
- Keep parallel reviewers via `pi-subagents`.

## Out of Scope (for MVP)

- Sophisticated conditional branching inside chains (beyond a small number of chain variants).
- Major changes to retry escalation semantics.
- Large rework of `tf-workflow` artifacts format.
