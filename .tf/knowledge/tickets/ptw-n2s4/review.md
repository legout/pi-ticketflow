# Review: ptw-n2s4

## Critical (must fix)
- `tf_cli/_version.py:6` - **No error handling for missing VERSION file**. If the package is installed via pip (non-editable) without the VERSION file, `import tf_cli` will raise `FileNotFoundError`. 
  - **Fix**: Wrap file read in try/except with fallback to `"unknown"`.
  - **Sources**: reviewer-general, reviewer-second-opinion

- `pyproject.toml` / **Missing MANIFEST.in** - The VERSION file is not configured to be included in the built package. The `tool.setuptools.packages = ["tf_cli"]` only includes the Python package directory, not files at repo root.
  - **Fix**: Add `MANIFEST.in` with `include VERSION`.
  - **Source**: reviewer-second-opinion

## Major (should fix)
- `pyproject.toml:7` - **Dynamic version may show 0.0.0 in pip**. Editable install may need reinstall for dynamic version to take effect.
  - **Fix**: Document need for `pip install -e .` reinstall or verify configuration.
  - **Source**: reviewer-second-opinion

## Minor (nice to fix)
- `package.json:3` - Hardcoded version instead of dynamically derived from VERSION file. Creates drift risk despite being consistent now.
  - **Source**: reviewer-spec-audit

- `tf_cli/_version.py` - No dedicated unit tests for this module.
  - **Source**: reviewer-general

- `VERSIONING.md:42-46` - npm version sync documentation is misleading since package.json has `"private": true` and won't be published.
  - **Source**: reviewer-second-opinion

## Warnings (follow-up ticket)
- `package.json` - Manual sync requirement noted; consider pre-commit hook or build script automation.
- `tf_cli/_version.py` vs `tf_cli/cli.py:get_version()` - Two different version reading methods could diverge.
- Missing `CHANGELOG.md` - Part of seed vision but not in ticket AC.
- `tf_cli/_version.py` - Version reading at import time can cause performance issues.
- **Dual version sources** - doctor check doesn't verify `tf_cli.__version__` matches VERSION.

## Suggestions (follow-up ticket)
- Use `importlib.metadata.version()` as fallback for installed packages.
- Add CI check verifying VERSION, package.json, pyproject.toml versions are in sync.
- Cache version at build time or use `functools.lru_cache` on `get_version()`.
- Add `version:sync` npm script to automate package.json sync.
- Add version consistency check to `tf doctor` command.

## Summary Statistics
- Critical: 2
- Major: 1
- Minor: 3
- Warnings: 5
- Suggestions: 5
