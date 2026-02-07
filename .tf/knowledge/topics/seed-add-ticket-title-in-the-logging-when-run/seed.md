# Seed: Add ticket title in verbose logging for `tf ralph`

## Vision

When running the Ralph loop in verbose mode, it's currently easy to lose context because logs tend to reference only ticket IDs or low-level actions. Showing the ticket **title** in verbose logs should make runs easier to understand, debug, and audit.

## Core Concept

Propagate ticket metadata (at least `id` + `title`) into Ralph’s logging context and update the verbose log formatting to include the title consistently.

## Key Features

1. In `tf ralph --verbose`, include ticket title in log prefixes/headers (e.g., `TKT-123 "Fix flaky tests"`).
2. Keep default (non-verbose) output unchanged to avoid extra noise.
3. Graceful fallback when a title is unavailable (show ID only, or `"<unknown title>"`).
4. Stable formatting that remains readable and reasonably parseable.

## Open Questions

- Where should Ralph source the title from (ticket cache, `tk` lookup, existing ticket list output)?
- Should title fetching be cached per ticket to avoid repeated subprocess calls?
- Do we need to support a machine-readable mode (JSONL) where title is a separate field?
- What redaction rules apply (e.g., titles may contain sensitive info)?
