---
id: ptw-guj5
status: closed
deps: []
links: []
created: 2026-02-05T14:17:14Z
type: task
priority: 2
assignee: legout
tags: [tf, enhancement, ptw-5pax-followup]
---
# Add version checking to legacy bash doctor implementation - The legacy bash doctor doesn't include version checking, creating a feature gap between tf doctor (legacy) and tf new doctor (Python). Users running standard tf doctor won't see version consistency checks.


## Notes

**2026-02-05T16:08:25Z**

Added version checking to legacy bash doctor (scripts/tf_legacy.sh).

Features:
- Checks consistency between package.json and VERSION file
- --fix flag to auto-fix VERSION file
- --dry-run flag to preview changes
- Normalizes version strings (strips v/V prefix)

All test scenarios passed. Implementation matches Python doctor functionality.

**2026-02-07T15:50:41Z**

Implemented version checking in legacy bash doctor (scripts/tf_legacy.sh):

- Added support for pyproject.toml, Cargo.toml, and package.json manifests
- Added git tag version checking with v/V prefix normalization
- Added VERSION file sync with --fix and --dry-run support
- Multi-manifest version mismatch detection (warns but doesn't fail)
- Priority order: pyproject.toml > Cargo.toml > package.json

Fixed issues from review:
- Added python3 availability checks in all version getter functions
- Improved TOML parsing to handle dotted keys (project.version)
- Refactored detect_manifest_versions to use pipe-delimited format instead of newlines

Commit: bfafb36
Artifacts: .tf/knowledge/tickets/ptw-guj5/

**2026-02-07T17:04:12Z**

Implemented comprehensive version checking in legacy bash doctor (scripts/tf_legacy.sh).

Changes:
- Added get_pyproject_version() for Python projects
- Added get_cargo_version() for Rust projects  
- Added get_git_tag_version() for git tag validation
- Enhanced check_version_consistency() with multi-manifest support
- Added scripts/tf_legacy.sh to install manifest

Features:
- Supports pyproject.toml, Cargo.toml, package.json (in priority order)
- VERSION file sync with --fix/--dry-run flags
- Git tag validation when on tagged commits
- Version normalization (v/V prefix stripping)
- Mismatch warnings between manifests

Commit: 1636cd9
