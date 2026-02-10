# Fixes: pt-9uxj

## Summary
Addressed parsing robustness issues, under-fix detection vulnerability, and procedure clarity in post-fix verification.

## Fixes by Severity

### Critical (must fix)
No critical issues found.

### Major (should fix)

#### 1. `tf/post_fix_verification.py:parse_fixes_counts()` - Under-fix detection vulnerability
**Issue**: The function assumes each bullet point represents exactly one fixed issue. Fixers may write compound fixes like "- Fixed 3 Critical issues in file.ts" as a single bullet.

**Fix Applied**:
- Added regex pattern to detect "Fixed (\d+)" or "(\d+) issues" patterns within bullet text
- Falls back to bullet counting when no explicit count found
- Added `extract_fix_count_from_text()` helper function

**Lines modified**: 125-180

#### 2. `tf/post_fix_verification.py:parse_fixes_counts()` - Silent failure on malformed fixes.md
**Issue**: If fixes.md exists but has no recognizable severity sections, the function returns `(counts, True)` with all-zero counts, potentially blocking tickets incorrectly.

**Fix Applied**:
- Added validation check after parsing
- If fixes.md exists but parsed fixed counts sum to zero, issue a warning
- Warning is written to the post-fix-verification.md artifact
- Added `fixes_parse_warning` field to `PostFixVerification` dataclass

**Lines modified**: 140-165, 195-210

#### 3. `.pi/skills/tf-workflow/SKILL.md` - Inconsistent prerequisite check
**Issue**: Post-Fix Verification procedure skips if `enableFixer` is false, but should run when quality gate is enabled regardless of fixer state.

**Fix Applied**:
- Changed prerequisite check from "Skip if `enableFixer` is false" to:
  - If `enableFixer` is false but `fixes.md` exists (manual fixes), run verification
  - If `enableFixer` is false and no `fixes.md`, write verification with "No fixes applied (fixer disabled)"
  - Removed the early skip condition

**Lines modified**: 446-450

### Minor (nice to fix)

#### 4. `tf/post_fix_verification.py:78` - Case-sensitive severity key lookup
**Issue**: Severity lookups may fail if different parts of the system use different casing.

**Fix Applied**:
- Normalized all severity keys to canonical case (first letter capitalized)
- Added `_canonicalize_severity()` helper function
- Applied normalization in both `parse_review_counts()` and `parse_fixes_counts()`

**Lines modified**: 78-95, 140-155

#### 5. `tf/post_fix_verification.py:197-200` - Race condition on file reads
**Issue**: Review.md and fixes.md are read separately; concurrent modifications could cause inconsistent counts.

**Fix Applied**:
- Added file timestamps to post-fix-verification.md artifact
- Added warning if timestamps differ by more than 1 second
- Uses file `stat` to capture mtime before parsing

**Lines modified**: 197-220, 245-260

#### 6. `tf/post_fix_verification.py:260-275` - Inefficient re-parsing
**Issue**: `get_quality_gate_counts()` re-parses the entire markdown file on every quality gate check.

**Fix Applied**:
- Added JSON sidecar file `post-fix-verification.json` with structured counts
- `get_quality_gate_counts()` now reads JSON first (fast) and falls back to markdown parsing
- JSON is written atomically alongside markdown

**Lines modified**: 260-310

## Summary Statistics
- **Critical**: 0
- **Major**: 3
- **Minor**: 3
- **Warnings**: 0
- **Suggestions**: 0

## Verification
- Syntax checked all modified Python files
- SKILL.md frontmatter validated
- Tested parsing logic against sample markdown formats
