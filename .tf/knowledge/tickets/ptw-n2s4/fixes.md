# Fixes: ptw-n2s4

## Critical Issues Fixed

### 1. Missing Error Handling in _version.py
**File**: `tf_cli/_version.py`
**Issue**: No error handling for missing VERSION file, causing `FileNotFoundError` on import.
**Fix**: Wrapped file read in `try/except` with fallback to `"unknown"`.

```python
def _read_version() -> str:
    """Read version from VERSION file with fallback."""
    try:
        with open(os.path.join(_ROOT, "VERSION")) as f:
            return f.read().strip()
    except (FileNotFoundError, IOError):
        return "unknown"
```

**Verification**: 
```bash
python -c "from tf_cli import __version__; print(__version__)"  # Output: 0.1.0
# Test fallback when VERSION missing: returns 'unknown'
```

### 2. VERSION File Not Included in Package
**File**: `MANIFEST.in` (created)
**Issue**: VERSION file at repo root not included in built package (wheel/sdist).
**Fix**: Created `MANIFEST.in` with `include VERSION` directive.

## Minor Issues Fixed

### 3. VERSIONING.md npm Documentation
**File**: `VERSIONING.md`
**Issue**: npm version sync documentation was misleading since package.json has `"private": true`.
**Fix**: Added note that sync is "for documentation consistency; package is private".

## Files Changed for Fixes
- `tf_cli/_version.py` - Added error handling
- `MANIFEST.in` - Created to include VERSION in package
- `VERSIONING.md` - Minor documentation update

## Verification
- Import with VERSION present: ✓ returns "0.1.0"
- Import with VERSION missing: ✓ returns "unknown"
- Package structure includes VERSION file via MANIFEST.in
