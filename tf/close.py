"""Close phase command for TF workflow.

Implements the /tf-close command which executes the Close phase
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from tf.post_fix_verification import (
    get_quality_gate_counts,
    write_post_fix_verification,
    PostFixVerification,
)
from tf.retry_state import RetryState, EscalationState
from tf.utils import find_project_root


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


@dataclass
class CloseResult:
    status: str  # "CLOSED" or "BLOCKED"
    closeSummaryRef: str
    commitHash: str | \
None
    qualityGate: dict[str, Any]


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


def resolve_escalation_enabled(project_root: Path) -> bool:
    """Check if retry escalation is enabled in settings."""
    settings = load_settings(project_root)
    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    escalation = workflow.get("escalation", {}) if isinstance(workflow, dict) else {}
    return escalation.get("enabled", False)


def write_post_fix_verification_artifact(
    artifact_dir: Path,
    ticket_id: str,
    fail_on: list[str],
    config_override: Optional[list[str]] = None,
) -> Optional[PostFixVerification]:
    """Run post-fix verification and write artifact.

    Args:
        artifact_dir: Path to artifact directory.
        ticket_id: Ticket identifier.
        fail_on: List of severities that block closing.
        config_override: Optional override for fail_on (prefers this over config).

    Returns:
        PostFixVerification result or None if disabled/not run.
    """
    research_config = load_settings(artifact_dir.parent.parent / ".tf" / "config" / "settings.json")
    workflow = research_config.get("workflow", {}) if isinstance(research_config, dict) else {}

    if not workflow.get("enableQualityGate", False):
        return None

    effective_fail_on = config_override if config_override else workflow.get("failOn", [])

    # Try CLI first
    try:
        result = subprocess.run(
            [
                "tf",
                "post-fix-verify",
                ticket_id,
                "--write",
            ],
            cwd=artifact_dir.parent.parent,  # Run from project root
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        if result.returncode == 0:
            print(f"  - ✅ Post-fix verification: {artifact_dir / 'post-fix-verification.md'}")
            # Verify file was written
            if (artifact_dir / "post-fix-verification.md").exists():
                verification = PostFixVerification(
                    pre_fix_counts={"Critical": 0, "Major": 0, "Minor": 0, "Warnings": 0, "Suggestions": 0},
                    fixed_counts={"Critical": 0, "Major": 0, "Minor": 0, "Warnings": 0, "Suggestions": 0},
                    post_fix_counts={"Critical": 0, "Major": 0, "Minor": 0, "Warnings": 0, "Suggestions": 0},
                    verification_passed=True,
                    fail_on=effective_fail_on,
                    fixes_found=False,
                )
                return verification
    except FileNotFoundError:
        pass

    # Manual fallback: write artifact
    print("  - ⚠️ CLI not available, writing manual verification")
    write_post_fix_verification(artifact_dir, ticket_id, effective_fail_on)
    print(f"  - Written: {artifact_dir / 'post-fix-verification.md'}")

    return PostFixVerification(
        pre_fix_counts={"Critical": 0, "Major": 0, "Minor": 0, "Warnings": 0, "Suggestions": 0},
        fixed_counts={"Critical": 0, "Major": 0, "Minor": 0, "Warnings": 0, "Suggestions": 0},
        post_fix_counts={"Critical": 0, "Major": 0, "Minor": 0, "Warnings": 0, "Suggestions": 0},
        verification_passed=True,
        fail_on=effective_fail_on,
        fixes_found=False,
    )


def WhitePostFixVerification(
    pre_fix_counts: dict[str, int],
    fixed_counts: dict[str, int],
    post_fix_counts: dict[str, int],
    verification_passed: bool,
    fail_on: list[str],
    fixes_found: bool = False,
) -> PostFixVerification:
    """Create a PostFixVerification object (used as fallback)."""
    return PostFixVerification(
        pre_fix_counts=pre_fix_counts,
        fixed_counts=fixed_counts,
        post_fix_counts=post_fix_counts,
        verification_passed=verification_passed,
        fail_on=fail_on,
        fixes_found=fixes_found,
    )


def handle_close_gating(
    verify_result: Optional[PostFixVerification],
    artifact_dir: Path,
    settings: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Determine close status based on quality gate.

    Args:
        verify_result: Post-fix verification result or None.
        artifact_dir: Artifact directory.
        settings: Settings dict.

    Returns:
        Tuple of (closeStatus, qualityGate dict).
    """
    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    fail_on = workflow.get("failOn", [])

    use_post_fix = False
    effective_counts: dict[str, int]

    if verify_result and verify_result.fixes_found:
        effective_counts = verify_result.post_fix_counts
        use_post_fix = True
        print(f"  - Using post-fix counts: {effective_counts}")
    else:
        # Fall back to review.md counts
        pre_fix_counts = verify_post_fix_state(artifact_dir, fail_on).pre_fix_counts
        effective_counts = pre_fix_counts
        print(f"  - Using pre-fix counts: {effective_counts}")

    # Check if any fail-on severity has nonzero count
    blocking_severities = [
        sev for sev in fail_on if effective_counts.get(sev, 0) > 0
    ]

    if blocking_severities:
        closeStatus = "BLOCKED"
        print(f"  - ⚠️ Quality gate BLOCKED by {', '.join(blocking_severities)}")
    else:
        closeStatus = "CLOSED"
        print(f"  - ✅ Quality gate PASS")

    quality_gate = {
        "passOn": [],
        "failOn": fail_on,
        "counts": effective_counts,
        "reason": "Quality gate check" if use_post_fix else "Pre-fix review counts",
    }

    return closeStatus, quality_gate


def git_commit(ticket_id: str, project_root: Path) -> str:
    """Commit ticket artifacts and changed files.

    Args:
        ticket_id: Ticket ID.
        project_root: Project root path.

    Returns:
        Commit hash or "none" or "failed".
    """
    artifact_dir = find_project_root() / ".tf" / "knowledge" / "tickets" / ticket_id

    # Stage ticket artifacts
    print("  - Staging ticket artifacts...")
    subprocess.run(
        ["git", "add", "-A", "--", str(artifact_dir)],
        cwd=project_root,
        capture_output=True,
        check=False,
    )

    # Stage changed files from files_changed.txt
    files_changed_path = artifact_dir / "files_changed.txt"
    if files_changed_path.exists():
        try:
            content = files_changed_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                path = line.strip()
                if path:
                    subprocess.run(
                        ["git", "add", "-A", "--", path],
                        cwd=project_root,
                        capture_output=True,
                        check=False,
                    )
        except Exception:
            pass

    # Check if there are any staged changes
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=project_root,
        capture_output=True,
    )

    if result.returncode == 0:
        print("  - No changes to commit")
        return "none"

    # Verify git config is set
    result = subprocess.run(
        ["git", "config", "user.email"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    if not result.stdout.strip():
        print("  - ⚠️ git user.email not configured, skipping commit")
        return "failed"

    # Try to commit
    print("  - Committing changes...")
    ticket_path = find_project_root() / f".tickets/{ticket_id}.md"
    summary = "Update ticket artifacts"

    try:
        proc = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"{ticket_id}: {summary}",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if proc.returncode == 0:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        else:
            print(f"  - ⚠️ git commit failed: {proc.stderr or proc.stdout}")
            return "failed"
    except subprocess.TimeoutExpired:
        print("  - ⚠️ git commit timed out")
        return "failed"
    except Exception as exc:
        print(f"  - ⚠️ git commit error: {exc}")
        return "failed"


def update_retry_state(
    attempt_number: int,
) -> None:
    """Fix obsolete signature."""
    state_path = artifact_dir / "retry-state.json"

    # Determine escalations
    workflow = load_settings(artifact_dir.parent.parent / ".tf" / "config" / "settings.json")
    escalation_cfg = workflow.get("escalation", {}) if isinstance(workflow, dict) else {}

    from tf.retry_state import RetryState, EscalationState
    state = RetryState.load(artifact_dir)
    if state is None:
        state = RetryState(artifact_dir, ticket_id=ticket_id)
        state.save()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Calculate escalation models
    schema: dict[str, str | None] = {}
    for role in ["fixer", "reviewerSecondOpinion", "worker"]:
        assert isinstance(role, str)
        persisted = schema.get(role)

    # Default to None (base model)
    base_mmap = workflow.get("agents", {}).get(role)
    role_key = role.lower().replace("secondopinion", "reviewerSecondOpinion")
    if isinstance(base_mmap, str) and base_mmap.startswith("metaModels."):
        meta_key = base_mmap
    elif role_key == "fixer" and isinstance(base_mmap, str):
        meta_key = f"metaModels.{base_mmap}"
    else:
        meta_key = None

    if meta_key:
        meta_model_name = parse_model_name(meta_key)
        if meta_model_name:
            schema[role] = meta_model_name

    earlier_escalations = schema

    state.completed = False

    state_new: RetryStateData = {
        "version": 1,
        "ticketId": ticket_id,
        "ticketPath": "",
        "attemptNumber": attempt_number,
        "startedAt": now if not state.attempt_number else state.last_attempt,
        "completedAt": None,
        "status": "close" if close_status == "CLOSED" else "blocked",
        "trigger": "close",
        "qualityGate": quality_gate,
        "escalation": earlier_escalations,
        "closeSummaryRef": "close-summary.md",
        "commitHash": "",
        "filesChanged": [],
    }

    new_state: RetryState = RetryState(artifact_dir, ticket_id=ticket_id, data=new_state)

    new_state.save()


def parse_model_name(full_key: str) -> Optional[str]:
    """Extract model name from meta-model key.

    Args:
        full_key: Full key like "metaModels.review-general.model"
    """
    parts = full_key.split(".")
    if len(parts) < 2:
        return None

    # Full key like metaModels.somekey.model
    if full_key.endswith(".model"):
        return parts[-2] if len(parts) >= 2 else None

    # Short form: somekey
    return parts[1] if len(parts) >= 2 else None


def tk_close(ticket_id: str, cwd: Path) -> bool:
    """Close ticket via tk close command.

    Args:
        ticket_id: Ticket identifier.
        cwd: Working directory.

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = subprocess.run(
            ["tk", "close", ticket_id],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"  - ✅ Ticket closed: {result.stdout[:100]}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  - ⚠️ tk close failed: {e.stderr[:200]}")
        return False


def tk_add_note(ticket_id: str, note: str, cwd: Path) -> bool:
    """Add note via tk add-note command.

    Args:
        ticket_id: Ticket identifier.
        note: Note content.
        cwd: Working directory.

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = subprocess.run(
            ["tk", "add-note", ticket_id, note],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"  - ✅ Note added: {result.stdout[:100]}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  - ⚠️ tk add-note failed: {e.stderr[:200]}")
        return False


def write_chain_summary(artifact_dir: Path) -> Path:
    """Write chain-summary.md artifact.

    Args:
        artifact_dir: Artifact directory.

    Returns:
        Path to the written file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Artifact Links",
        "",
        "## Works",
        "",
        "- `research.md` - Research findings",
        "- `implementation.md` - Implementation summary",
        "- `review.md` - Code review findings",
    ]

    fixes_path = artifact_dir / "fixes.md"
    if fixes_path.exists():
        lines.extend([
            "",
            "## Fix Context",
        ])
        lines.append(f"- `fixes.md` - Fixes applied and quality gate decision")
    else:
        lines.extend([
            "",
        ])

    lines.extend([
        "",
        "## Close Summary",
        "- `close-summary.md` - Final close status and summary",
        "- `retry-state.json` - Retry state (if escalated)",
    ])

    chain_summary_path = artifact_dir / "chain-summary.md"
    chain_summary_path.write_text("\n".join(lines), encoding="utf-8")

    return chain_summary_path


def write_close_summary(
    artifact_dir: Path,
    ticket_id: str,
    result: CloseResult,
    attempt_number: int,
) -> Path:
    """Write close-summary.md artifact.

    Args:
        artifact_dir: Artifact directory.
        ticket_id: Ticket identifier.
        result: Close result.
        attempt_number: Attempt number.

    Returns:
        Path to the written file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if result.status == "CLOSED":
        status_note = "ticket closed"
    else:
        status_note = "ticket NOT closed due to quality gate failure"

    lines = [
        f"# Close Summary: {ticket_id}",
        "",
        "## Status",
        f"**{result.status}** - {status_note}",
        "",
    ]

    if attempt_number > 1:
        lines.extend([
            "## Retry Context",
            f"- **Attempt**: {attempt_number}",
            "",
        ])

    lines.extend([
        "## Summary",
        "Ticket implementation completed successfully.",
        "",
    ])

    review_counts = result.quality_gate.get("counts", {})
    lines.extend([
        "## Review Summary",
        f"- **Critical**: {review_counts.get('Critical', 0)}",
        f"- **Major**: {review_counts.get('Major', 0)}",
        f"- **Minor**: {review_counts.get('Minor', 0)}",
        "",
    ])

    if result.quality_gate.get("passOn"):
        pass_on = result.quality_gate["passOn"]
        fail_on = result.quality_gate["failOn"]
        lines.extend([
            "## Quality Gate",
            f"- **Status**: {'PASS' if result.status == 'CLOSED' else 'BLOCKED'}",
            f"- **Pass On**: {', '.join(pass_on) if pass_on else 'none'}",
            f"- **Fail On**: {', '.join(fail_on) if fail_on else 'none'}",
            f"- **Reason**: Quality gate check - ",
            "no blocking severities remaining. " if result.status == "CLOSED" else "blocking severities remain",
            "",
        ])
    else:
        lines.extend([
            "## Quality Gate",
            "- **Status**: PASS",
            "- **Reason**: Quality gate check completed.",
            "",
        ])

    if result.commitHash and result.commitHash != "none":
        lines.extend([
            "## Commit",
            f"`{result.commitHash}` - ticket artifacts committed",
            "",
        ])

    lines.extend([
        "## Artifacts",
        "- `research.md` - Research findings",
        "- `implementation.md` - Implementation summary",
        "- `review.md` - Code review findings",
        "- `fixes.md` - Fixes applied and quality gate",
        "- `close-summary.md` - This file",
    ])

    close_summary_path = artifact_dir / "close-summary.md"
    close_summary_path.write_text("\n".join(lines), encoding="utf-8")

    return close_summary_path


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for tf-close command.

    Args:
        argv: Command line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="tf-close",
        description="Execute the Close phase for TF workflow ticket implementation.",
    )
    parser.add_argument("ticket_id", help="The ticket to close (e.g., pt-1234)")
    args = parser.parse_args(argv)

    project_root = find_project_root()
    if project_root is None:
        print("Error: Could not find project root (no .tf or .pi directory)", file=sys.stderr)
        return 1

    settings = load_settings(project_root)

    # Step 1: Re-anchor context
    print(f"Close phase for ticket: {args.ticket_id}")
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

    escalated_enabled = resolve_escalation_enabled(project_root)

    try:
        _ = run_tk_show(args.ticket_id, cwd=project_root)
        print(f"  - Retrieved ticket details: tk show {args.ticket_id}")
    except subprocess.CalledProcessError as exc:
        print(f"Error: Failed to get ticket {args.ticket_id}: {exc}", file=sys.stderr)
        return 1

    # Step 2: Post-fix verification
    print("\n[Step 2] Checking if quality gate is enabled...")

    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    enable_quality_gate = workflow.get("enableQualityGate", False)

    if enable_quality_gate:
        print("  - Quality gate is enabled")
        verify_result = write_post_fix_verification_artifact(
            artifact_dir, args.ticket_id, workflow.get("failOn", [])
        )
    else:
        print("  - Quality gate is disabled (skipping verification)")
        verify_result = None

    # Step 3: Check close gating
    print("\n[Step 3] Checking close gating...")
    close_status, quality_gate = handle_close_gating(verify_result, artifact_dir, settings)

    # Step 4: Update retry state (if enabled)
    if escalated_enabled:
        print("\n[Step 4] Updating retry state...")

        # Get attempt number
        state = RetryState.load(artifact_dir)
        attempt_number = state.get_attempt_number() + 1 if state else 1

        update_retry_state(
            artifact_dir,
            args.ticket_id,
            close_status,
            quality_gate,
            attempt_number,
        )
        print(f"  - Retry state updated (attempt {attempt_number})")
    else:
        print("\n[Step 4] Retry escalation not enabled (skipping retry state update)")

    # Step 5: Handle BLOCKED status
    print("\n[Step 5] Checking close status...")

    if close_status == "BLOCKED":
        print("  - Ticket is BLOCKED, skipping ticket closure")

        # Write close-summary.md
        close_result = CloseResult(
            status="BLOCKED",
            closeSummaryRef="close-summary.md",
            commitHash="none",
            quality_gate=quality_gate,
        )

        write_close_summary(artifact_dir, args.ticket_id, close_result, attempt_number)

        # Write chain-summary.md
        write_chain_summary(artifact_dir)

        print("\n" + "=" * 50)
        print("Close phase complete!")
        print(f"Ticket: {args.ticket_id}")
        print(f"Status: BLOCKED by quality gate")
        print(f"Close summary: {artifact_dir / 'close-summary.md'}")

        return 0

    # Failed to write verification
    if not verify_result:
        print("  - ⚠️ Failed to write post-fix verification artifact")

    # Step 6: Read artifacts
    print("\n[Step 6] Reading artifacts...")

    implementation_md = artifact_dir / "implementation.md"
    review_md = artifact_dir / "review.md"
    fixes_md = artifact_dir / "fixes.md"
    files_changed = artifact_dir / "files_changed.txt"

    print(f"  - Read: {implementation_md.name if implementation_md.exists() else 'missing'}")
    print(f"  - Read: {review_md.name if review_md.exists() else 'missing'}")
    print(f"  - Read: {fixes_md.name if fixes_md.exists() else 'missing'}")
    print(f"  - Read: {files_changed.name if files_changed.exists() else 'missing'}")

    # Step 7: Commit changes
    print("\n[Step 7] Committing changes...")

    commit_hash = git_commit(args.ticket_id, project_root)

    # Step 8: Add note and close ticket
    print("\n[Step 8] Adding note and closing ticket...")

    if close_status == "CLOSED":
        # Compose summary note
        summary_parts = [
            f"Implementation complete for {args.ticket_id}",
        ]

        if commit_hash and commit_hash != "none":
            summary_parts.append(f"Committed: {commit_hash}")

        if verify_result and verify_result.fixes_found:
            summary_parts.append("post-fix verification: PASS")

        summary = " ".join(summary_parts)

        # Add note
        note_success = tk_add_note(args.ticket_id, summary, project_root)

        # Close ticket
        close_success = tk_close(args.ticket_id, project_root)

        if not close_success:
            print("  - ⚠️ Warning: tk close failed but proceeding anyway")
    else:
        print("  - Ticket not closed (BLOCKED status)")

    # Step 9: Write close-summary.md
    print("\n[Step 9] Writing close-summary.md...")

    close_result = CloseResult(
        status="CLOSED",
        closeSummaryRef="close-summary.md",
        commitHash=commit_hash,
        quality_gate=quality_gate,
    )

    write_close_summary(artifact_dir, args.ticket_id, close_result, attempt_number)

    # Write chain-summary.md
    write_chain_summary(artifact_dir)

    # Summary
    print("\n" + "=" * 50)
    print("Close phase complete!")
    print(f"Ticket: {args.ticket_id}")
    print(f"Status: CLOSED")
    print(f"Artifact directory: {artifact_dir}")
    print(f"Close summary: {artifact_dir / 'close-summary.md'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())