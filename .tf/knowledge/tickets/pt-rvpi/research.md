# Research: pt-rvpi

## Status
Research enabled. Minimal research performed - ticket is straightforward implementation of internal logging utility.

## Context Reviewed
- `tk show pt-rvpi` - Ticket requirements
- `/home/volker/coding/pi-ticketflow/tf_cli/ralph_new.py` - Existing Ralph code with LogLevel enum
- `/home/volker/coding/pi-ticketflow/.tf/knowledge/topics/seed-add-more-logging-to-ralph-loop/` - Seed context

## Key Findings
1. Ralph already has a `LogLevel` enum (QUIET, NORMAL, VERBOSE, DEBUG)
2. Current code uses `print()` statements directly to stdout/stderr
3. Log level resolution exists in `resolve_log_level()` function
4. Need to centralize logging into a helper class

## Requirements Summary
- Helper with levels: info/warn/error/debug
- Timestamps in ISO format
- Context fields: ticket id, iteration, mode (serial/parallel)
- Output to stderr by default
- Redaction helper for secrets and large values

## Sources
- Seed: seed-add-more-logging-to-ralph-loop
- Ticket: pt-rvpi
