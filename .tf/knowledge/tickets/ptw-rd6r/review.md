# Review: ptw-rd6r

## Critical (must fix)
- None

## Major (should fix)
- `tf_cli/doctor_new.py:61-101` - `read_toml` only strips full-line comments but leaves inline comments attached to values. Lines like `version = "1.2.3"  # release` produce values containing the comment text, which corrupts version detection and causes false mismatch warnings. The parser must strip inline comments (while respecting quotes) before interpreting values.
  - Sources: reviewer-general, reviewer-second-opinion

- `tf_cli/doctor_new.py:472-533` - The mismatch/git-tag/VERSION warnings print `found_manifests[0]` as the canonical manifest even when the highest-priority manifest exists but lacks a valid version. When pyproject.toml exists but has no version, the canonical comes from Cargo/package.json, but warnings still name pyproject.toml. The actual manifest that produced `canonical_version` must be tracked and displayed.
  - Sources: reviewer-general, reviewer-spec-audit, reviewer-second-opinion

## Minor (nice to fix)
- `tf_cli/doctor_new.py:597-607` - The `--fix` flag help text still mentions syncing to `package.json`, but the doctor now uses the highest-priority manifest (pyproject.toml/Cargo.toml/package.json). Update the description to reflect multi-language behavior.
  - Sources: reviewer-general, reviewer-spec-audit

## Warnings (follow-up ticket)
- None

## Suggestions (follow-up ticket)
- None

## Summary Statistics
- Critical: 0
- Major: 2
- Minor: 1
- Warnings: 0
- Suggestions: 0

## Reviewers
- reviewer-general: 2 Major, 1 Minor
- reviewer-spec-audit: 1 Major, 1 Minor
- reviewer-second-opinion: 2 Major, 0 Minor
