"""Fix phase command for TF workflow.

Implements the /tf-fix command which executes the Fix phase
for ticket implementation according to the tf-workflow specification.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from tf.retry_state import RetryState
from tf.utils import find_project_root


SEVERITY_ORDER = {
    "Critical": 0,
    "Major": 1,
    "Minor": 2,
    "Warnings": 3,
    "Suggestions": 4,
}

SEVERITY_FIX_ORDER = ["Critical", "Major", "Minor"]

SEVERITY_TITLES = {
    "Critical": "### Critical (must fix)",
    "Major": "### Major (should fix)",
    "Minor": "### Minor (nice to fix)",
    "Warnings": "### Warnings (follow-up)",
    "Suggestions": "### Suggestions (follow-up)",
}


@dataclass
class Issue:
    severity: str
    location: str
    description: str
    fixed: bool = False
    fix_note: str = ""


def load_settings(project_root: Path) -> dict[str, Any]:
    """Load settings from project config files.

    Args:
        project_root: Project root path.

    Returns:
        Parsed settings dict or empty dict.
    """
    candidates = [
        project_root / ".tf" / "config" / "settings.json",
        project_root / "config" / "settings.json",
    ]

    for path in candidates:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            continue

    return {}


def read_agents_md(project_root: Path) -> Optional[str]:
    """Read root AGENTS.md file if it exists."""
    path = project_root / "AGENTS.md"
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def read_ralph_agents_md_if_referenced(project_root: Path, agents_content: Optional[str]) -> Optional[str]:
    """Read .tf/ralph/AGENTS.md when root AGENTS references it."""
    if not agents_content:
        return None

    if ".tf/ralph/AGENTS.md" not in agents_content:
        return None

    path = project_root / ".tf" / "ralph" / "AGENTS.md"
    if not path.exists():
        return None

    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def resolve_knowledge_dir(project_root: Path, settings: dict[str, Any]) -> Path:
    """Resolve knowledge directory from config (default .tf/knowledge)."""
    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    raw = workflow.get("knowledgeDir", ".tf/knowledge")

    path = Path(raw)
    if not path.is_absolute():
        path = project_root / path
    return path


def run_tk_show(ticket_id: str, cwd: Path) -> str:
    """Run tk show and return ticket details."""
    result = subprocess.run(
        ["tk", "show", ticket_id],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def is_fixer_enabled(settings: dict[str, Any]) -> bool:
    """Check if fixer is enabled in config."""
    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    return workflow.get("enableFixer", True)


def resolve_escalated_models(
    artifact_dir: Path,
    settings: dict[str, Any],
) -> dict[str, str | None]:
    """Resolve escalated models from retry-state for current attempt."""
    state = RetryState.load(artifact_dir)
    if state is None:
        return {
            "fixer": None,
            "reviewerSecondOpinion": None,
            "worker": None,
        }

    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    escalation_cfg = workflow.get("escalation", {}) if isinstance(workflow, dict) else {}

    # Resolve base fixer model from agents config
    base_fixer = _resolve_fixer_model_from_config(settings)
    base_models = {
        "fixer": base_fixer,
        "reviewerSecondOpinion": None,
        "worker": None,
    }

    next_attempt_number = state.get_attempt_number() + 1

    escalated = state.resolve_escalation(
        escalation_cfg,
        base_models,
        next_attempt_number=next_attempt_number,
    )

    return {
        "fixer": escalated.fixer,
        "reviewerSecondOpinion": escalated.reviewerSecondOpinion,
        "worker": escalated.worker,
    }


def _resolve_fixer_model_from_config(settings: dict[str, Any]) -> str | None:
    """Resolve fixer model from config."""
    agents = settings.get("agents", {}) if isinstance(settings, dict) else {}
    meta_models = settings.get("metaModels", {}) if isinstance(settings, dict) else {}

    fixer_key = agents.get("fixer")
    if not fixer_key:
        return None

    if isinstance(fixer_key, str) and isinstance(meta_models.get(fixer_key), dict):
        mm = meta_models[fixer_key]
        model = mm.get("model")
        if isinstance(model, str):
            return model

    # Direct model id path
    if isinstance(fixer_key, str) and "/" in fixer_key:
        return fixer_key

    return None


def parse_review_issues(review_content: str) -> list[Issue]:
    """Parse issues from review.md content.

    Args:
        review_content: The review.md content.

    Returns:
        List of Issue objects.
    """
    issues: list[Issue] = []
    section_for_line: str | None = None

    section_regexes = {
        "Critical": re.compile(r"^##\s*Critical\b", re.IGNORECASE),
        "Major": re.compile(r"^##\s*Major\b", re.IGNORECASE),
        "Minor": re.compile(r"^##\s*Minor\b", re.IGNORECASE),
        "Warnings": re.compile(r"^##\s*Warnings\b", re.IGNORECASE),
        "Suggestions": re.compile(r"^##\s*Suggestions\b", re.IGNORECASE),
    }

    for raw in review_content.splitlines():
        line = raw.rstrip()

        # Check for section headers
        matched_section = None
        for sev, pattern in section_regexes.items():
            if pattern.match(line):
                matched_section = sev
                break

        if matched_section is not None:
            section_for_line = matched_section
            continue

        # Reset section on other headers
        if line.startswith("## "):
            section_for_line = None
            continue

        # Skip non-bullet lines
        if section_for_line not in SEVERITY_ORDER:
            continue

        stripped = line.strip()
        
        # Skip standalone "None" entries (not bullet items)
        if stripped.lower() in {"none", "none."}:
            continue
        
        if not stripped.startswith("-"):
            continue

        bullet = stripped.lstrip("-").strip()

        # Skip "None" or "No issues found" entries
        lowered = bullet.lower()
        if lowered in {"none", "none.", "no issues found", "no issues found."}:
            continue

        location, description = _split_location_and_description(bullet)
        if not description:
            description = bullet

        issues.append(
            Issue(
                severity=section_for_line,
                location=location,
                description=description,
            )
        )

    return issues


def _split_location_and_description(bullet: str) -> tuple[str, str]:
    """Split a bullet into location and description."""
    # Prefer backtick location: `path:line` - description
    m = re.match(r"`([^`]+)`\s*-\s*(.+)$", bullet)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Fallback: path:line - description
    m = re.match(r"([^\s]+:\d+)\s*-\s*(.+)$", bullet)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Generic split on first hyphen
    if " - " in bullet:
        left, right = bullet.split(" - ", 1)
        left = left.strip().strip("`")
        right = right.strip()
        if left and right:
            return left, right

    return "unknown", bullet.strip()


def count_issues_by_severity(issues: list[Issue]) -> dict[str, int]:
    """Count issues by severity."""
    counts = {sev: 0 for sev in SEVERITY_ORDER}
    for issue in issues:
        if issue.severity in counts:
            counts[issue.severity] += 1
    return counts


def has_fixable_issues(issues: list[Issue]) -> bool:
    """Check if there are any Critical, Major, or Minor issues."""
    for issue in issues:
        if issue.severity in ["Critical", "Major", "Minor"]:
            return True
    return False


def read_review_md(artifact_dir: Path) -> Optional[str]:
    """Read review.md if it exists."""
    review_path = artifact_dir / "review.md"
    if not review_path.exists():
        return None
    try:
        return review_path.read_text(encoding="utf-8")
    except Exception:
        return None


def read_files_changed(artifact_dir: Path) -> list[str]:
    """Read files_changed.txt if it exists."""
    files_path = artifact_dir / "files_changed.txt"
    if not files_path.exists():
        return []
    try:
        content = files_path.read_text(encoding="utf-8")
        return [line.strip() for line in content.splitlines() if line.strip()]
    except Exception:
        return []


def write_files_changed(artifact_dir: Path, files: list[str]) -> Path:
    """Write files_changed.txt atomically."""
    artifact_dir.mkdir(parents=True, exist_ok=True)

    files_path = artifact_dir / "files_changed.txt"
    temp_path = files_path.with_suffix(".tmp")

    content = "\n".join(files) + "\n" if files else ""
    temp_path.write_text(content, encoding="utf-8")

    os.replace(str(temp_path), str(files_path))
    return files_path


def track_file(project_root: Path, filepath: str, files_changed_path: Path) -> None:
    """Track a file in files_changed.txt."""
    try:
        subprocess.run(
            ["tf", "track", filepath, "--file", str(files_changed_path)],
            cwd=project_root,
            capture_output=True,
            check=False,
        )
    except Exception:
        # Fallback: append directly
        files_changed_path.parent.mkdir(parents=True, exist_ok=True)
        existing = set()
        if files_changed_path.exists():
            existing = set(
                line.strip()
                for line in files_changed_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        if filepath not in existing:
            with files_changed_path.open("a", encoding="utf-8") as f:
                f.write(f"{filepath}\n")


def run_tests(project_root: Path) -> dict[str, Any]:
    """Run tests for the project.

    Returns:
        Dictionary with test results.
    """
    results = {
        "run": False,
        "passed": True,
        "output": "",
        "command": "",
    }

    test_commands = [
        ("pytest", ["pytest", "-v"]),
        ("python -m pytest", ["python", "-m", "pytest", "-v"]),
        ("npm test", ["npm", "test"]),
        ("cargo test", ["cargo", "test"]),
        ("go test", ["go", "test", "./..."]),
    ]

    for name, cmd in test_commands:
        executable = cmd[0]
        if not (project_root / executable.replace("python", "python3").split()[0]).exists():
            # Check if command is available
            import shutil
            if not shutil.which(executable.replace("python", "python3").split()[0]):
                continue

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=300,
            )
            results["run"] = True
            results["passed"] = proc.returncode == 0
            results["output"] = (proc.stdout + "\n" + proc.stderr).strip()
            results["command"] = " ".join(cmd)
            break
        except subprocess.TimeoutExpired:
            results["run"] = True
            results["passed"] = False
            results["output"] = f"Test command timed out: {name}"
            results["command"] = " ".join(cmd)
            break
        except FileNotFoundError:
            continue
        except Exception as e:
            results["run"] = True
            results["passed"] = False
            results["output"] = f"Error running tests: {e}"
            results["command"] = " ".join(cmd)
            break

    return results


def write_fixes_md(
    artifact_dir: Path,
    ticket_id: str,
    issues: list[Issue],
    fixer_enabled: bool,
    test_results: dict[str, Any],
    escalated_model: str | None,
) -> Path:
    """Write fixes.md artifact.

    Args:
        artifact_dir: Directory to write the artifact.
        ticket_id: The ticket ID.
        issues: List of issues from review.
        fixer_enabled: Whether fixer was enabled.
        test_results: Test results after fixes.
        escalated_model: Escalated model for fixer (if any).

    Returns:
        Path to the written file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Fixes: {ticket_id}",
        "",
    ]

    if not fixer_enabled:
        lines.extend([
            "## Summary",
            "Fixer is disabled via configuration. No fixes were applied.",
            "",
            "## Note",
            "To enable fixer, set `workflow.enableFixer: true` in `.tf/config/settings.json`.",
            "",
            "## Summary Statistics",
            "- **Critical**: 0",
            "- **Major**: 0",
            "- **Minor**: 0",
            "- **Warnings**: 0",
            "- **Suggestions**: 0",
            "",
        ])
    elif not has_fixable_issues(issues):
        lines.extend([
            "## Summary",
            "No fixes needed. Review contained no Critical/Major/Minor issues.",
            "",
            "## Summary Statistics",
            "- **Critical**: 0",
            "- **Major**: 0",
            "- **Minor**: 0",
            "- **Warnings**: 0",
            "- **Suggestions**: 0",
            "",
        ])
    else:
        # Group issues by severity
        by_severity: dict[str, list[Issue]] = {sev: [] for sev in SEVERITY_ORDER}
        for issue in issues:
            by_severity[issue.severity].append(issue)

        lines.extend([
            "## Summary",
            "Fixes applied based on review feedback.",
            "",
        ])

        if escalated_model:
            lines.extend([
                "## Retry Context",
                f"- Escalated Fixer Model: {escalated_model}",
                "",
            ])

        lines.append("## Fixes by Severity")
        lines.append("")

        # Write fixable issues
        for severity in SEVERITY_FIX_ORDER:
            sev_issues = by_severity.get(severity, [])
            if not sev_issues:
                continue

            lines.append(SEVERITY_TITLES[severity])
            lines.append("")
            for issue in sev_issues:
                checkbox = "[x]" if issue.fixed else "[ ]"
                fix_note = f" - {issue.fix_note}" if issue.fix_note else ""
                lines.append(f"- {checkbox} `{issue.location}` - {issue.description}{fix_note}")
            lines.append("")

        # Write non-fixable issues (Warnings/Suggestions)
        for severity in ["Warnings", "Suggestions"]:
            sev_issues = by_severity.get(severity, [])
            if not sev_issues:
                continue

            lines.append(SEVERITY_TITLES[severity])
            lines.append("")
            for issue in sev_issues:
                lines.append(f"- [ ] `{issue.location}` - {issue.description} (deferred to follow-up)")
            lines.append("")

        # Count fixed issues
        fixed_counts = {sev: 0 for sev in SEVERITY_FIX_ORDER}
        for issue in issues:
            if issue.fixed and issue.severity in fixed_counts:
                fixed_counts[issue.severity] += 1

        lines.extend([
            "## Summary Statistics",
            f"- **Critical**: {fixed_counts['Critical']}",
            f"- **Major**: {fixed_counts['Major']}",
            f"- **Minor**: {fixed_counts['Minor']}",
            "- **Warnings**: 0",
            "- **Suggestions**: 0",
            "",
        ])

    # Add verification section
    lines.extend([
        "## Verification",
    ])

    if test_results["run"]:
        status = "✅ Passed" if test_results["passed"] else "❌ Failed"
        lines.append(f"- Tests: {status} ({test_results['command']})")
        if not test_results["passed"] and test_results["output"]:
            lines.append(f"  ```")
            lines.append(test_results["output"][:500])
            lines.append(f"  ```")
    else:
        lines.append("- No tests detected or run")

    lines.append("")

    fixes_path = artifact_dir / "fixes.md"
    fixes_path.write_text("\n".join(lines), encoding="utf-8")
    return fixes_path


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for tf-fix command.

    Args:
        argv: Command line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="tf-fix",
        description="Execute the Fix phase for TF workflow ticket implementation.",
    )
    parser.add_argument("ticket_id", help="The ticket to fix (e.g., pt-1234)")
    args = parser.parse_args(argv)

    project_root = find_project_root()
    if project_root is None:
        print("Error: Could not find project root (no .tf or .pi directory)", file=sys.stderr)
        return 1

    settings = load_settings(project_root)

    # Step 1: Re-anchor context
    print(f"Fix phase for ticket: {args.ticket_id}")
    print("\n[Step 1] Re-anchoring context...")

    root_agents = read_agents_md(project_root)
    if root_agents:
        print("  - Read root AGENTS.md")
        ralph_agents = read_ralph_agents_md_if_referenced(project_root, root_agents)
        if ralph_agents:
            print("  - Read .tf/ralph/AGENTS.md (referenced)")

    knowledge_dir = resolve_knowledge_dir(project_root, settings)
    artifact_dir = knowledge_dir / "tickets" / args.ticket_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    print(f"  - Artifact dir: {artifact_dir}")

    escalated_models = resolve_escalated_models(artifact_dir, settings)
    if escalated_models.get("fixer"):
        print(f"  - Escalated fixer model: {escalated_models['fixer']}")

    try:
        _ = run_tk_show(args.ticket_id, cwd=project_root)
        print(f"  - Retrieved ticket details: tk show {args.ticket_id}")
    except subprocess.CalledProcessError as exc:
        print(f"Error: Failed to get ticket {args.ticket_id}: {exc}", file=sys.stderr)
        return 1

    # Step 2: Check if fixer is enabled
    print("\n[Step 2] Checking if fixer is enabled...")
    fixer_enabled = is_fixer_enabled(settings)
    if fixer_enabled:
        print("  - Fixer is enabled")
    else:
        print("  - Fixer is disabled via config")

    # Step 3: Check review issues
    print("\n[Step 3] Checking review issues...")
    review_content = read_review_md(artifact_dir)
    if not review_content:
        print("  - Warning: review.md not found, creating empty fix record")
        issues: list[Issue] = []
    else:
        issues = parse_review_issues(review_content)
        counts = count_issues_by_severity(issues)
        print(
            f"  - Issues: Critical={counts['Critical']}, Major={counts['Major']}, "
            f"Minor={counts['Minor']}, Warnings={counts['Warnings']}, Suggestions={counts['Suggestions']}"
        )

    if not has_fixable_issues(issues):
        print("  - No fixable issues (Critical/Major/Minor) found")

    # Step 4: Fix issues
    print("\n[Step 4] Applying fixes...")

    if not fixer_enabled or not has_fixable_issues(issues):
        print("  - Skipping fix phase (disabled or no fixable issues)")
        test_results = {"run": False, "passed": True, "output": "", "command": ""}
    else:
        print("  - This phase is executed by the AI agent")
        print("  - The agent should fix issues in priority order:")
        print("    1. Critical (must fix)")
        print("    2. Major (should fix)")
        print("    3. Minor (fix if low effort)")
        print("  - Warnings and Suggestions should NOT be fixed (become follow-ups)")

        # Read current files_changed.txt
        changed_files = read_files_changed(artifact_dir)
        print(f"  - Currently tracking {len(changed_files)} changed files")

        # Note: The actual fixing is done by the AI agent
        # For now, mark all fixable issues as not fixed
        # (The agent will update this when it applies fixes)
        for issue in issues:
            if issue.severity in ["Critical", "Major", "Minor"]:
                issue.fixed = False
                issue.fix_note = "Pending fix by AI agent"

        test_results = {"run": False, "passed": True, "output": "", "command": ""}

    # Step 5: Re-run tests
    print("\n[Step 5] Running tests...")
    if fixer_enabled and has_fixable_issues(issues):
        test_results = run_tests(project_root)
        if test_results["run"]:
            if test_results["passed"]:
                print(f"  - ✅ Tests passed ({test_results['command']})")
            else:
                print(f"  - ⚠️ Tests failed ({test_results['command']})")
        else:
            print("  - No tests detected")
    else:
        print("  - Skipping tests (no fixes applied)")

    # Step 6: Write fixes.md
    print("\n[Step 6] Writing fixes.md...")

    fixes_path = write_fixes_md(
        artifact_dir,
        args.ticket_id,
        issues,
        fixer_enabled,
        test_results,
        escalated_models.get("fixer"),
    )
    print(f"  - Written: {fixes_path}")

    # Summary
    print("\n" + "=" * 50)
    print("Fix phase complete!")
    print(f"Ticket: {args.ticket_id}")
    print(f"Artifact directory: {artifact_dir}")
    print(f"Fixes artifact: {fixes_path}")

    if not fixer_enabled:
        print("\nNote: Fixer was disabled via configuration.")
    elif not has_fixable_issues(issues):
        print("\nNote: No fixable issues were found in review.")
    else:
        print("\nNote: Actual fixes should be applied by the AI agent.")
        print("      The agent should update fixes.md with applied fixes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
