"""CLI command for post-fix verification.

This module provides a command to manually run post-fix verification
on a ticket artifact directory.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from tf.post_fix_verification import (
    get_quality_gate_counts,
    verify_post_fix_state,
    write_post_fix_verification,
)


def load_config(project_path: Optional[Path] = None) -> dict:
    """Load TF configuration from settings.json.

    Args:
        project_path: Optional project root path

    Returns:
        Configuration dictionary
    """
    search_paths = []
    if project_path:
        search_paths.append(project_path / ".tf" / "config" / "settings.json")
    if os.environ.get("TF_REPO_ROOT"):
        search_paths.append(
            Path(os.environ["TF_REPO_ROOT"]) / ".tf" / "config" / "settings.json"
        )
    search_paths.append(Path.cwd() / ".tf" / "config" / "settings.json")

    for path in search_paths:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
    return {}


def resolve_knowledge_dir(config: dict, project_path: Optional[Path] = None) -> Path:
    """Resolve knowledge directory from config or defaults.

    Args:
        config: Loaded configuration
        project_path: Optional project root path

    Returns:
        Path to knowledge directory
    """
    knowledge_dir = config.get("workflow", {}).get("knowledgeDir", ".tf/knowledge")

    if project_path:
        return project_path / knowledge_dir
    if os.environ.get("TF_REPO_ROOT"):
        return Path(os.environ["TF_REPO_ROOT"]) / knowledge_dir
    return Path.cwd() / knowledge_dir


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run post-fix verification for a ticket."
    )
    parser.add_argument("ticket_id", help="Ticket ID (e.g., pt-abc123)")
    parser.add_argument(
        "--project",
        help="Project root path (defaults to current directory)",
    )
    parser.add_argument(
        "--knowledge-dir",
        help="Knowledge base directory (overrides config)",
    )
    parser.add_argument(
        "--artifact-dir",
        help="Direct path to artifact directory (overrides ticket_id lookup)",
    )
    parser.add_argument(
        "--fail-on",
        help="Comma-separated severities that block (overrides config)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write post-fix-verification.md artifact",
    )
    parser.add_argument(
        "--counts-only",
        action="store_true",
        help="Only output the counts for quality gate decision",
    )

    args = parser.parse_args(argv)

    # Load configuration
    project_path = Path(args.project) if args.project else None
    config = load_config(project_path)

    # Resolve artifact directory
    if args.artifact_dir:
        artifact_dir = Path(args.artifact_dir)
    else:
        knowledge_dir = (
            Path(args.knowledge_dir)
            if args.knowledge_dir
            else resolve_knowledge_dir(config, project_path)
        )
        artifact_dir = knowledge_dir / "tickets" / args.ticket_id

    if not artifact_dir.exists():
        print(f"Error: Artifact directory not found: {artifact_dir}", file=sys.stderr)
        return 1

    # Check for required review.md
    review_path = artifact_dir / "review.md"
    if not review_path.exists():
        print(f"Error: review.md not found in {artifact_dir}", file=sys.stderr)
        return 1

    # Resolve fail_on severities
    if args.fail_on:
        fail_on = [s.strip() for s in args.fail_on.split(",")]
    else:
        fail_on = config.get("workflow", {}).get("failOn", ["Critical", "Major"])

    # Check if quality gate is enabled
    enable_gate = config.get("workflow", {}).get("enableQualityGate", True)

    if args.counts_only:
        # Just get the counts for quality gate decision
        counts, source = get_quality_gate_counts(artifact_dir, fail_on)
        if args.json:
            result = {
                "counts": counts,
                "source": source,
                "fail_on": fail_on,
                "blocking": {sev: counts.get(sev, 0) for sev in fail_on if counts.get(sev, 0) > 0},
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Source: {source}")
            print(f"Fail on: {', '.join(fail_on)}")
            for sev, count in counts.items():
                marker = " (!)" if sev in fail_on and count > 0 else ""
                print(f"  {sev}: {count}{marker}")
            blocking = [sev for sev in fail_on if counts.get(sev, 0) > 0]
            if blocking:
                print(f"\nBlocked by: {', '.join(blocking)}")
            else:
                print("\nQuality gate: PASSED")
        return 0

    # Run full verification
    verification = verify_post_fix_state(artifact_dir, fail_on)

    # Write artifact if requested
    if args.write:
        output_path = write_post_fix_verification(artifact_dir, args.ticket_id, fail_on)
        print(f"Written: {output_path}")

    # Output results
    if args.json:
        result = {
            "ticket_id": args.ticket_id,
            "verification_passed": verification.verification_passed,
            "fail_on": fail_on,
            "pre_fix_counts": verification.pre_fix_counts,
            "fixed_counts": verification.fixed_counts,
            "post_fix_counts": verification.post_fix_counts,
            "fixes_found": verification.fixes_found,
            "enable_quality_gate": enable_gate,
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Ticket: {args.ticket_id}")
        print(f"Quality Gate: {'enabled' if enable_gate else 'disabled'}")
        print(f"Fail on: {', '.join(fail_on)}")
        print()
        print("Pre-fix counts:")
        for sev, count in verification.pre_fix_counts.items():
            print(f"  {sev}: {count}")
        print()
        if verification.fixes_found:
            print("Fixed counts:")
            for sev, count in verification.fixed_counts.items():
                print(f"  {sev}: {count}")
            print()
        print("Post-fix counts:")
        for sev, count in verification.post_fix_counts.items():
            marker = " (!)" if sev in fail_on and count > 0 else ""
            print(f"  {sev}: {count}{marker}")
        print()
        if verification.verification_passed:
            print("Status: PASSED - no blocking severities remain")
        else:
            blocking = [sev for sev in fail_on if verification.post_fix_counts.get(sev, 0) > 0]
            print(f"Status: BLOCKED by {', '.join(blocking)}")

    return 0 if verification.verification_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
