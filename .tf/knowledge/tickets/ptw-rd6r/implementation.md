# Implementation: ptw-rd6r

## Summary
Extended version check to support multi-language projects. Added support for reading versions from Python (pyproject.toml) and Rust (Cargo.toml) package manifests, in addition to the existing Node.js (package.json) support.

## Files Changed
- `tf_cli/doctor_new.py` - Added TOML parsing and multi-language version detection
- `tests/test_doctor_version.py` - Added comprehensive tests for new functionality

## Key Changes

### 1. TOML Parser (`read_toml`)
Added a lightweight TOML parser that handles:
- Section headers (`[section]` and `[section.subsection]`)
- String values with single/double quotes
- Boolean values (true/false)
- Integer values
- Full-line comments (lines starting with #)

### 2. New Version Getters
- `get_pyproject_version()` - Reads version from `[project]` section per PEP 621
- `get_cargo_version()` - Reads version from `[package]` section
- `detect_manifest_versions()` - Detects all available manifests and returns:
  - Canonical version (from highest priority manifest with valid version)
  - List of found manifests
  - Dictionary of all manifest versions

### 3. Manifest Priority Order
1. `pyproject.toml` (Python) - highest priority
2. `Cargo.toml` (Rust)
3. `package.json` (Node.js) - lowest priority

### 4. Multi-Manifest Warnings
When multiple manifests exist with different versions, the system:
- Uses the first valid version as canonical (by priority order)
- Warns about version mismatches between manifests
- Still reports all found manifests and their versions

### 5. VERSION File Sync
The `--fix` flag now syncs the VERSION file with the canonical manifest version, regardless of which manifest type is the source.

## Tests Added
- `TestGetPyprojectVersion` - 6 tests for Python manifest parsing
- `TestGetCargoVersion` - 6 tests for Rust manifest parsing
- `TestReadToml` - 5 tests for TOML parser functionality
- `TestDetectManifestVersions` - 5 tests for multi-manifest detection
- `TestMultiLanguageVersionCheck` - 5 tests for end-to-end multi-language scenarios

Total: 71 tests (all passing)

## Verification
Run the version check:
```bash
tf doctor              # Check version consistency
tf doctor --fix        # Sync VERSION file with canonical manifest
tf doctor --dry-run    # Preview changes without applying
```

## Example Output
```
Version consistency:
[ok] pyproject.toml version: 2.0.0
[ok] package.json version: 1.0.0
[warn] Version mismatch between package manifests:
       Canonical (first valid): pyproject.toml = 2.0.0
       Mismatch: package.json = 1.0.0
       Consider aligning versions across all manifests
[info] No VERSION file found (optional)
```
