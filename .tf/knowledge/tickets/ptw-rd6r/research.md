# Research: ptw-rd6r - Multi-language version check

## Task
Extend version check to support multi-language projects - Check version consistency across pyproject.toml, Cargo.toml, and other package manifests.

## Current State
The `doctor_new.py` module currently only supports:
- `package.json` (Node.js/npm) - canonical source
- `VERSION` file - optional sync target

## Target Package Manifests

### Python: pyproject.toml
- Standard: PEP 621 (pyproject.toml format)
- Version location: `[project]` table, `version` field
- Example:
  ```toml
  [project]
  name = "my-project"
  version = "1.2.3"
  ```
- Also supports dynamic version (to ignore)

### Rust: Cargo.toml
- Standard: Cargo manifest format
- Version location: `[package]` table, `version` field
- Example:
  ```toml
  [package]
  name = "my-project"
  version = "1.2.3"
  ```

### Node.js: package.json (existing)
- Version location: root `version` field
- Already implemented

## Implementation Strategy
1. Create generic `get_project_version(project_root)` that tries all manifest types
2. Support priority order: pyproject.toml → Cargo.toml → package.json
3. Continue supporting VERSION file sync
4. Detect multi-manifest situations (warn if multiple found)
5. Add tests for new manifest parsers

## Files to Modify
- `tf_cli/doctor_new.py` - Add new parsers and update check logic
- `tests/test_doctor_version.py` - Add tests for new functionality
