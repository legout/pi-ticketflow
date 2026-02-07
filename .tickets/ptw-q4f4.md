---
id: ptw-q4f4
status: closed
deps: []
links: []
created: 2026-02-05T14:44:27Z
type: task
priority: 3
assignee: legout
tags: [tf, followup]
---
# Add more pytest markers for test categorization

## Origin
From review of: ptw-0un2
File: pyproject.toml

## Issue
Consider adding more markers for test categorization (e.g., unit, e2e, smoke) to enable better test filtering.

## Current Markers
- slow
- integration

## Proposed Additional Markers
- unit: fast unit tests
- e2e: end-to-end tests
- smoke: quick smoke tests

## Acceptance Criteria
- [ ] New markers defined in pyproject.toml
- [ ] Existing tests categorized with appropriate markers


## Notes

**2026-02-05T17:08:35Z**

Added pytest markers for test categorization: unit (231 tests), e2e (2 tests), smoke (3 tests). Also marked existing integration tests (15 tests). All markers registered and tests passing. Commit: 0afd3e3
