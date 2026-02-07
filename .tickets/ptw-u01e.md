---
id: ptw-u01e
status: closed
deps: []
links: []
created: 2026-02-05T14:17:14Z
type: task
priority: 2
assignee: legout
tags: [tf, enhancement, ptw-5pax-followup]
---
# Extend version check to support git tags as third version source - Verify package.json version matches git tag for release validation.


## Notes

**2026-02-05T16:29:22Z**

Implemented git tag version check.

Changes:
- Added get_git_tag_version() to read version from current git tag
- Updated check_version_consistency() to validate against git tags
- Git tags are normalized (v prefix stripped) for consistent comparison
- Shows [ok] when tag matches, [warn] when mismatched
- 7 new tests added, all 71 tests pass

Commit: a38acfd
