# Assumptions

- The workflow resolves a "meta-model key" (e.g. `planning`, `worker`, `fast`) into a concrete model id.
- The `agents.fixer` mapping is the canonical place to choose which meta-model the fixer uses.
- Backward compatibility is required because existing repos/settings may not define a `fixer` meta-model.
