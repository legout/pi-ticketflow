---
id: ptw-u91i
status: closed
deps: []
links: []
created: 2026-02-05T14:44:27Z
type: task
priority: 3
assignee: legout
tags: [tf, followup]
---
# Add HTML coverage report to pytest defaults

## Origin
From review of: ptw-0un2
File: pyproject.toml

## Issue
Consider adding coverage HTML reports to the default addopts for easier local debugging of coverage gaps.

## Proposed Change
Add '--cov-report=html' to [tool.pytest.ini_options] addopts

## Acceptance Criteria
- [ ] HTML coverage report generated on test runs
- [ ] Report directory added to .gitignore


## Notes

**2026-02-05T17:09:39Z**

## Implementation Complete

**Changes:**
- Added  to  in pyproject.toml
- Added  to .gitignore

**Commit:** e44e9bb2e9aaa1a0f84d9b9c7ce723b90c56f3df

**Verification:**
- TOML syntax validated successfully
- HTML coverage reports will now be generated on test runs
- Report directory properly ignored by git
