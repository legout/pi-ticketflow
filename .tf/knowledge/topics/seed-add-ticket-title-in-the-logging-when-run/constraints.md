# Constraints

- Avoid adding many subprocess calls (or network calls) inside tight loops; prefer caching.
- Do not change default output unless explicitly in `--verbose` mode.
- Keep formatting consistent and readable across terminals.
- If titles might contain sensitive information, define how to handle/redact them (at least document the behavior).
