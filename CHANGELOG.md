# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure and CLI tooling.

## [0.1.0] - 2026-02-05

### Added

- Initial release of `pi-tk-workflow` (Ticketflow CLI).
- Core CLI commands: `create`, `ready`, `next`, `show`, `close`, `add-note`, `link`.
- Ticket management system with YAML-based storage.
- Seed-driven planning workflow for capturing and refining ideas.
- Research phase with support for external spec references (OpenSpec).
- IRF (Implement-Review-Fix) workflow with parallel reviews.
- Subagent-based reviewer system with general, spec-audit, and second-opinion reviewers.
- Fixer agent for addressing review findings.
- Quality gate with configurable severity thresholds.
- Ralph autonomous loop for batch ticket processing.
- Progress tracking and lessons learned capture.
- Python CLI with Click framework.
- pytest-based test suite with coverage reporting.
- Configuration system via `.tf/config/settings.json`.

### Changed

- N/A

### Deprecated

- N/A

### Removed

- N/A

### Fixed

- N/A

### Security

- N/A

[unreleased]: https://github.com/volker/pi-tk-workflow/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/volker/pi-tk-workflow/releases/tag/v0.1.0
