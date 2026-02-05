# Review (Second Opinion): ptw-n2s4

## Overall Assessment
The implementation correctly establishes VERSION as the canonical source and creates a clean `__version__` export pattern. However, there are critical packaging issues that will cause runtime failures when the package is installed (not in editable mode), and error handling is missing for the version file read operation.

## Critical (must fix)
- `tf_cli/_version.py:5-6` - **No error handling for missing VERSION file**. If the package is installed via pip (non-editable) without the VERSION file being included, `import tf_cli` will raise `FileNotFoundError` at runtime. This breaks the package for end users.
  - **Fix**: Wrap the file read in try/except and provide a fallback like `"unknown"` or use `importlib.metadata` as a fallback.
  - **Why**: Files at repo root are not automatically included in Python packages; the VERSION file must either be explicitly included or the code must handle its absence.

- `pyproject.toml` / **Missing MANIFEST.in** - The VERSION file is not configured to be included in the built package (wheel/sdist). The `tool.setuptools.packages = ["tf_cli"]` only includes the Python package directory, not files at the repo root.
  - **Fix**: Add a `MANIFEST.in` file with `include VERSION`, or configure `tool.setuptools.package-data` to include the VERSION file.
  - **Why**: Without this, `pip install` will install a broken package that cannot import successfully.

## Major (should fix)
- `pyproject.toml:7` - **Dynamic version shows 0.0.0 in pip**. Running `pip show pi-tk-workflow` displays `Version: 0.0.0` despite VERSION file containing `0.1.0`. This suggests the editable install may not have reloaded the dynamic version configuration properly, or there's a caching issue.
  - **Why**: Users and tools rely on `pip show` to verify installed versions. The discrepancy is confusing.

## Minor (nice to fix)
- `VERSIONING.md:42-46` - **npm version sync documentation is misleading**. The package.json has `"private": true`, meaning it won't be published to npm. The documented npm version sync procedure adds complexity for a package that never gets published.
  - **Suggestion**: Clarify that npm version is for documentation only since the package is private.

## Warnings (follow-up ticket)
- `tf_cli/_version.py` / **Version reading at import time**. Reading a file at import time can cause performance issues and makes the module harder to test in isolation. Consider lazy loading or caching.

- **Dual version sources**. The project now has three version sources that could drift: VERSION file (canonical), `tf_cli._version.__version__` (runtime), and `pyproject.toml` dynamic version (build-time). The doctor check only validates package.json against VERSION, but doesn't verify `tf_cli.__version__` matches.

## Suggestions (follow-up ticket)
- **Consider importlib.metadata**. For a more robust approach, use `importlib.metadata.version("pi-tk-workflow")` as the primary method with VERSION file as fallback. This works correctly in both editable and installed modes.

- **Add version consistency check to doctor**. The `tf doctor` command should verify that `tf_cli.__version__` matches the VERSION file, catching the critical issue above.

## Positive Notes
- Clean separation of version reading logic into dedicated `_version.py` module
- Good documentation in VERSIONING.md explaining the bump procedure
- `pyproject.toml` correctly uses dynamic versioning to eliminate duplication
- The `__all__` export in `__init__.py` is properly defined

## Summary Statistics
- Critical: 2
- Major: 1
- Minor: 1
- Warnings: 2
- Suggestions: 2
