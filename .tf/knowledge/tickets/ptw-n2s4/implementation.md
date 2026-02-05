# Implementation: ptw-n2s4

## Summary
Established the VERSION file as the canonical source of truth for project versioning and made all package metadata consistent with it.

## Files Changed
- `pyproject.toml` - Changed from static `version = "0.0.0"` to `dynamic = ["version"]` with `version = {file = "VERSION"}`
- `tf_cli/_version.py` - Created new module to read version from VERSION file at runtime
- `tf_cli/__init__.py` - Added `__version__` export for package consumers
- `VERSIONING.md` - Created documentation explaining the versioning scheme and bump procedure

## Key Decisions
1. **VERSION file as canonical source**: Chosen because it's language-agnostic and readable by both Python and Node.js tooling
2. **Dynamic versioning in pyproject.toml**: Uses setuptools dynamic version feature to read from file, eliminating duplication
3. **Manual sync for package.json**: For MVP, package.json version is documented as needing manual sync; future work could automate this

## Verification
```bash
# Verify Python can read version
python -c "from tf_cli import __version__; print(__version__)"
# Output: 0.1.0
```

## Notes
- pyproject.toml was previously at version `0.0.0` while VERSION and package.json were at `0.1.0` - now all are consistent
- No breaking changes; existing imports continue to work
