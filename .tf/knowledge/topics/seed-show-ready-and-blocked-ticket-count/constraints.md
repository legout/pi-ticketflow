# Constraints

- Avoid expensive recomputation (e.g., avoid repeatedly re-listing all tickets from disk/network if not necessary).
- Do not break existing `tk ralph` output contracts for scripts (if any). Prefer additive output or gated by flags.
- Ensure output behaves sensibly in both TTY and non-TTY environments.
