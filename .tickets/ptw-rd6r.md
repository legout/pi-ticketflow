---
id: ptw-rd6r
status: closed
deps: []
links: []
created: 2026-02-05T14:17:14Z
type: task
priority: 2
assignee: legout
tags: [tf, enhancement, ptw-5pax-followup]
---
# Extend version check to support multi-language projects - Check version consistency across pyproject.toml, Cargo.toml, and other package manifests.


## Notes

**2026-02-05T16:25:15Z**

--text 
## Implementation Complete

Extended version check to support multi-language projects.

### Changes
- Added TOML parser (read_toml) for parsing pyproject.toml and Cargo.toml
- Added get_pyproject_version() for Python projects (PEP 621)
- Added get_cargo_version() for Rust projects
- Added detect_manifest_versions() to detect all available manifests
- Updated check_version_consistency() to handle multi-manifest projects

### Manifest Priority
1. pyproject.toml (Python)
2. Cargo.toml (Rust)  
3. package.json (Node.js)

### Tests
- 64 tests total (all passing)
- 27 new tests for multi-language support

### Commit
33d45a1 ptw-rd6r: Extend version check to support multi-language projects

