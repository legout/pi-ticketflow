"""Post-fix verification for quality gate decisions.

This module provides functionality to verify the state of issues after fixes
have been applied, ensuring the quality gate checks the post-fix state rather
than the pre-fix review counts.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict


class SeverityCounts(TypedDict):
    """Severity count structure."""

    Critical: int
    Major: int
    Minor: int
    Warnings: int
    Suggestions: int


@dataclass
class FixEntry:
    """Single fix entry parsed from fixes.md."""

    severity: str
    file_path: str
    line: int | None
    description: str


@dataclass
class PostFixVerification:
    """Result of post-fix verification."""

    pre_fix_counts: dict[str, int]
    fixed_counts: dict[str, int]
    post_fix_counts: dict[str, int]
    verification_passed: bool
    fail_on: list[str]
    fixes_found: bool
    fixes_parse_warning: str | None = None
    review_mtime: float | None = None
    fixes_mtime: float | None = None

    def to_markdown(self, ticket_id: str) -> str:
        """Generate post-fix-verification.md content."""
        lines = [
            f"# Post-Fix Verification: {ticket_id}",
            "",
            "## Summary",
            f"- **Status**: {'PASS' if self.verification_passed else 'FAIL'}",
            f"- **Quality Gate**: blocks on {', '.join(self.fail_on)}",
        ]

        if self.fixes_parse_warning:
            lines.append(f"- **Warning**: {self.fixes_parse_warning}")

        if self.review_mtime is not None and self.fixes_mtime is not None:
            time_diff = abs(self.review_mtime - self.fixes_mtime)
            if time_diff > 1.0:
                lines.append(f"- **Note**: Source files differ by {time_diff:.1f}s (possible race condition)")

        lines.extend(["", "## Pre-Fix Counts (from review.md)"])

        for severity in ["Critical", "Major", "Minor", "Warnings", "Suggestions"]:
            count = self.pre_fix_counts.get(severity, 0)
            lines.append(f"- **{severity}**: {count}")

        lines.extend(["", "## Fixes Applied (from fixes.md)"])

        if self.fixes_found:
            for severity in ["Critical", "Major", "Minor", "Warnings", "Suggestions"]:
                count = self.fixed_counts.get(severity, 0)
                lines.append(f"- **{severity}**: {count}")
        else:
            lines.append("_No fixes.md found or no fixes applied_")

        lines.extend(["", "## Post-Fix Counts (calculated)"])

        for severity in ["Critical", "Major", "Minor", "Warnings", "Suggestions"]:
            count = self.post_fix_counts.get(severity, 0)
            lines.append(f"- **{severity}**: {count}")

        lines.extend(
            [
                "",
                "## Quality Gate Decision",
                f"- **Based on**: Post-fix counts" if self.fixes_found else "- **Based on**: Pre-fix counts (no fixes applied)",
            ]
        )

        # Determine blocking severities
        blocking = [
            sev
            for sev in self.fail_on
            if self.post_fix_counts.get(sev, 0) > 0
        ]

        if blocking:
            lines.append(f"- **Result**: BLOCKED by {', '.join(blocking)}")
        else:
            lines.append("- **Result**: PASSED - no blocking severities remain")

        lines.append("")
        return "\n".join(lines)

    def to_json_dict(self) -> dict:
        """Export as JSON-serializable dictionary."""
        return {
            "ticket_id": None,  # Set by caller
            "pre_fix_counts": self.pre_fix_counts,
            "fixed_counts": self.fixed_counts,
            "post_fix_counts": self.post_fix_counts,
            "verification_passed": self.verification_passed,
            "fail_on": self.fail_on,
            "fixes_found": self.fixes_found,
            "fixes_parse_warning": self.fixes_parse_warning,
            "review_mtime": self.review_mtime,
            "fixes_mtime": self.fixes_mtime,
        }


def _canonicalize_severity(severity: str) -> str:
    """Normalize severity to canonical case (first letter capitalized).

    Args:
        severity: Input severity string (e.g., "critical", "CRITICAL")

    Returns:
        Canonical severity string (e.g., "Critical")
    """
    severity_lower = severity.lower()
    canonical_map = {
        "critical": "Critical",
        "major": "Major",
        "minor": "Minor",
        "warnings": "Warnings",
        "suggestions": "Suggestions",
    }
    return canonical_map.get(severity_lower, severity.capitalize())


def _extract_fix_count_from_text(text: str) -> int | None:
    """Extract fix count from bullet text.

    Handles patterns like:
    - "Fixed 3 Critical issues"
    - "Fixed 2 issues in file.ts"
    - "3 issues fixed"

    Args:
        text: Bullet text to parse

    Returns:
        Count if found, None otherwise
    """
    # Pattern: "Fixed (\d+)" or "(\d+) issues"
    patterns = [
        r"(?:fixed|fixed\s*:\s*)(\d+)\s*(?:issues?|items?)?",
        r"(\d+)\s*(?:issues?|items?)\s*(?:fixed|resolved|completed)",
        r"(?:resolved|completed)\s*(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def parse_review_counts(review_path: Path) -> dict[str, int]:
    """Parse severity counts from review.md.

    Args:
        review_path: Path to review.md file

    Returns:
        Dictionary mapping severity names to counts
    """
    counts: dict[str, int] = {
        "Critical": 0,
        "Major": 0,
        "Minor": 0,
        "Warnings": 0,
        "Suggestions": 0,
    }

    if not review_path.exists():
        return counts

    content = review_path.read_text(encoding="utf-8")

    # Look for Summary Statistics section
    stats_match = re.search(
        r"##\s*Summary\s*Statistics.*?(?=\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )

    if stats_match:
        stats_section = stats_match.group(0)
        for severity in list(counts.keys()):  # Use list() to avoid dict change during iter
            sev_match = re.search(
                rf"(?:^|\s|[-*]\s*)(?:\*\*)?{re.escape(severity)}(?:\*\*)?\s*:\s*(\d+)",
                stats_section,
                re.IGNORECASE | re.MULTILINE,
            )
            if sev_match:
                canonical = _canonicalize_severity(severity)
                counts[canonical] = int(sev_match.group(1))

    return counts


def parse_fixes_counts(fixes_path: Path) -> tuple[dict[str, int], bool, str | None]:
    """Parse fixed issue counts from fixes.md.

    Args:
        fixes_path: Path to fixes.md file

    Returns:
        Tuple of (counts dict, found flag, warning message)
    """
    counts: dict[str, int] = {
        "Critical": 0,
        "Major": 0,
        "Minor": 0,
        "Warnings": 0,
        "Suggestions": 0,
    }

    if not fixes_path.exists():
        return counts, False, None

    content = fixes_path.read_text(encoding="utf-8")

    # Check if "No fixes needed" or fixer disabled
    if re.search(r"No fixes needed|fixer is disabled|No fixes applied", content, re.IGNORECASE):
        return counts, True, None

    # Parse fixed issues by severity section
    for severity in list(counts.keys()):
        # Match section headers like "## Fixed Critical" or "## Critical Fixes"
        pattern = rf"##\s*(?:Fixed\s+)?{re.escape(severity)}(?:\s+Fixed|s|\s+Issues)?(?:\s*\([^)]*\))?"
        section_match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)

        if section_match:
            section_start = section_match.end()
            next_header = re.search(r"\n^##\s", content[section_start:], re.MULTILINE)
            section_end = (
                section_start + next_header.start() if next_header else len(content)
            )
            section = content[section_start:section_end]

            # Count bullet items in section
            items = re.findall(r"\n-\s", section)
            item_count = len(items)

            # Also check for explicit counts in bullet text (e.g., "Fixed 3 issues")
            explicit_count = 0
            bullet_texts = re.findall(r"\n-\s+(.*)", section)
            for text in bullet_texts:
                extracted = _extract_fix_count_from_text(text)
                if extracted is not None:
                    explicit_count += extracted
                else:
                    explicit_count += 1  # Default to 1 per bullet

            # Use explicit count if different from simple bullet count
            canonical = _canonicalize_severity(severity)
            counts[canonical] = explicit_count if explicit_count > item_count else item_count

    # Validate: if fixes.md exists but we parsed zero counts, issue warning
    warning = None
    if sum(counts.values()) == 0:
        warning = "fixes.md found but no fix counts parsed - verify format matches expected structure"

    return counts, True, warning


def verify_post_fix_state(
    artifact_dir: Path | str,
    fail_on: list[str],
) -> PostFixVerification:
    """Verify post-fix state and determine quality gate result.

    This function:
    1. Reads review.md to get pre-fix counts
    2. Reads fixes.md to determine what was fixed
    3. Calculates post-fix counts (pre-fix - fixed)
    4. Determines if quality gate passes based on failOn severities

    Args:
        artifact_dir: Path to ticket artifact directory
        fail_on: List of severity levels that block closing

    Returns:
        PostFixVerification with counts and gate decision
    """
    path = Path(artifact_dir)
    review_path = path / "review.md"
    fixes_path = path / "fixes.md"

    # Capture file modification times before reading (for race condition detection)
    review_mtime = review_path.stat().st_mtime if review_path.exists() else None
    fixes_mtime = fixes_path.stat().st_mtime if fixes_path.exists() else None

    # Get pre-fix counts from review.md
    pre_fix_counts = parse_review_counts(review_path)

    # Get fixed counts from fixes.md
    fixed_counts, fixes_found, parse_warning = parse_fixes_counts(fixes_path)

    # Calculate post-fix counts
    post_fix_counts: dict[str, int] = {}
    for severity in ["Critical", "Major", "Minor", "Warnings", "Suggestions"]:
        remaining = max(0, pre_fix_counts.get(severity, 0) - fixed_counts.get(severity, 0))
        post_fix_counts[severity] = remaining

    # Determine if quality gate passes
    # If no fixes were found, use pre-fix counts (backwards compatible)
    effective_counts = post_fix_counts if fixes_found else pre_fix_counts
    blocking_severities = [
        sev for sev in fail_on if effective_counts.get(sev, 0) > 0
    ]
    verification_passed = len(blocking_severities) == 0

    return PostFixVerification(
        pre_fix_counts=pre_fix_counts,
        fixed_counts=fixed_counts,
        post_fix_counts=post_fix_counts,
        verification_passed=verification_passed,
        fail_on=fail_on,
        fixes_found=fixes_found,
        fixes_parse_warning=parse_warning,
        review_mtime=review_mtime,
        fixes_mtime=fixes_mtime,
    )


def write_post_fix_verification(
    artifact_dir: Path | str,
    ticket_id: str,
    fail_on: list[str],
) -> Path:
    """Write post-fix verification artifact.

    Args:
        artifact_dir: Path to ticket artifact directory
        ticket_id: Ticket identifier
        fail_on: List of severity levels that block closing

    Returns:
        Path to written markdown file
    """
    path = Path(artifact_dir)
    path.mkdir(parents=True, exist_ok=True)

    verification = verify_post_fix_state(path, fail_on)
    content = verification.to_markdown(ticket_id)

    output_path = path / "post-fix-verification.md"
    output_path.write_text(content, encoding="utf-8")

    # Also write JSON sidecar for efficient programmatic access
    json_path = path / "post-fix-verification.json"
    json_data = verification.to_json_dict()
    json_data["ticket_id"] = ticket_id
    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

    return output_path


def get_quality_gate_counts(
    artifact_dir: Path | str,
    fail_on: list[str],
) -> tuple[dict[str, int], str]:
    """Get counts for quality gate decision with post-fix verification.

    First tries to read the JSON sidecar for efficiency, then falls back
    to parsing the markdown file.

    Args:
        artifact_dir: Path to ticket artifact directory
        fail_on: List of severity levels that block closing

    Returns:
        Tuple of (counts dict, source description)
        Source is either "post-fix", "post-fix-json", or "pre-fix"
    """
    path = Path(artifact_dir)

    # Try JSON sidecar first (fastest)
    json_path = path / "post-fix-verification.json"
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            post_fix_counts = data.get("post_fix_counts", {})
            if post_fix_counts:
                return post_fix_counts, "post-fix-json"
        except (json.JSONDecodeError, OSError):
            pass  # Fall back to markdown parsing

    # Try markdown file
    verification_path = path / "post-fix-verification.md"
    if verification_path.exists():
        content = verification_path.read_text(encoding="utf-8")

        # Extract post-fix counts
        post_fix_counts: dict[str, int] = {}
        in_post_fix = False

        for line in content.split("\n"):
            if "## Post-Fix Counts" in line:
                in_post_fix = True
                continue
            if in_post_fix and line.startswith("##"):
                break
            if in_post_fix:
                match = re.search(r"-\s*\*\*(\w+)\*\*\s*:\s*(\d+)", line)
                if match:
                    severity, count = match.groups()
                    post_fix_counts[severity] = int(count)

        if post_fix_counts:
            return post_fix_counts, "post-fix"

    # Fall back to pre-fix counts from review.md
    review_path = path / "review.md"
    pre_fix_counts = parse_review_counts(review_path)
    return pre_fix_counts, "pre-fix"
