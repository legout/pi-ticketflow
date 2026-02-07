# Fixes: ptw-rd6r

## Issues Fixed

### Major Issue 1: Inline Comments in TOML Parser
**File**: `tf_cli/doctor_new.py:61-101`
**Problem**: The `read_toml` parser only stripped full-line comments but left inline comments attached to values. Lines like `version = "1.2.3"  # release` would include the comment text in the value.
**Fix**: Added inline comment stripping logic that respects quotes. The parser now finds the first `#` that is not inside quotes and strips everything from that position.

### Major Issue 2: Canonical Manifest Tracking
**File**: `tf_cli/doctor_new.py:297-330, 472-546`
**Problem**: Warning messages used `found_manifests[0]` as the canonical manifest name, even when the highest-priority manifest existed but lacked a valid version. This caused incorrect warnings (e.g., claiming pyproject.toml was canonical when package.json actually provided the version).
**Fix**: 
- Modified `detect_manifest_versions()` to return a 4-tuple including `canonical_manifest` (the actual manifest that provided the canonical version)
- Updated `check_version_consistency()` to use `canonical_manifest` instead of `found_manifests[0]` in all warning messages
- Updated tests to handle the new return signature

### Minor Issue: --fix Help Text
**File**: `tf_cli/doctor_new.py:620`
**Problem**: The help text still mentioned syncing to `package.json` instead of the canonical manifest.
**Fix**: Updated help text to: "Auto-fix VERSION file to match canonical manifest (pyproject.toml, Cargo.toml, or package.json)"

## Tests Added
- `TestReadToml.test_parses_inline_comments` - Verifies inline comments are stripped
- `TestReadToml.test_parses_inline_comments_with_hash_in_quotes` - Verifies # inside quoted strings is preserved
- Updated `TestDetectManifestVersions` tests to check `canonical_manifest` return value

## Test Results
- 73 tests passed (71 existing + 2 new)
- All quality checks completed
