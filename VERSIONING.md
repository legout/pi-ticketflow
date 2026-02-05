# Version Management

This document describes how versioning works in the Ticketflow project.

## Canonical Version Source

The single source of truth for the project version is:

```
VERSION
```

This plain text file contains only the version string (e.g., `0.1.0`).

## How Version is Used

### Python Package (`pyproject.toml`)
- Uses `dynamic = ["version"]` with `version = {file = "VERSION"}`
- No manual editing needed in pyproject.toml

### Python Code
- Import via: `from tf_cli import __version__`
- Reads from VERSION file at runtime

### Node.js Package (`package.json`)
- Currently has a hardcoded version field
- Must be manually synced when VERSION changes
- Future: could use a pre-publish script to read from VERSION

## Bumping the Version

To bump the version:

1. Edit the `VERSION` file:
   ```bash
   echo "0.2.0" > VERSION
   ```

2. Sync `package.json` (for documentation consistency; package is private):
   ```bash
   # Manual: edit package.json version field
   # Or use npm version:
   npm version $(cat VERSION) --no-git-tag-version --allow-same-version
   ```

3. Commit the changes:
   ```bash
   git add VERSION package.json
   git commit -m "Bump version to X.Y.Z"
   ```

## Version Format

We follow [SemVer](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes
