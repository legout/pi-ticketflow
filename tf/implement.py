"""Implementation phase command for TF workflow.

Implements the /tf-implement command which executes the Implementation phase
for ticket implementation according to the tf-workflow specification.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from tf.kb_helpers import resolve_knowledge_dir
from tf.retry_state import RetryState, load_escalation_config
from tf.utils import find_project_root


def load_workflow_config(project_root: Path) -> dict:
    """Load workflow configuration from settings.json.
    
    Args:
        project_root: Path to the project root.
        
    Returns:
        Dictionary with workflow configuration.
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
                return data.get("workflow", {})
        except Exception:
            continue

    return {}


def read_agents_md(project_root: Path) -> Optional[str]:
    """Read root AGENTS.md file if it exists.
    
    Args:
        project_root: Path to the project root.
        
    Returns:
        Content of AGENTS.md or None if not found.
    """
    agents_md = project_root / "AGENTS.md"
    if agents_md.exists():
        return agents_md.read_text(encoding="utf-8")
    return None


def read_ralph_agents_md(project_root: Path) -> Optional[str]:
    """Read .tf/ralph/AGENTS.md for lessons learned if referenced.
    
    Args:
        project_root: Path to the project root.
        
    Returns:
        Content of .tf/ralph/AGENTS.md or None if not found.
    """
    ralph_agents_md = project_root / ".tf" / "ralph" / "AGENTS.md"
    if ralph_agents_md.exists():
        return ralph_agents_md.read_text(encoding="utf-8")
    return None


def run_tk_show(ticket_id: str) -> str:
    """Run 'tk show' command to get ticket details.
    
    Args:
        ticket_id: The ticket ID to show.
        
    Returns:
        The ticket content as string.
        
    Raises:
        subprocess.CalledProcessError: If tk command fails.
    """
    result = subprocess.run(
        ["tk", "show", ticket_id],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def read_research_md(artifact_dir: Path) -> Optional[str]:
    """Read research.md artifact if it exists.
    
    Args:
        artifact_dir: Path to the artifact directory.
        
    Returns:
        Content of research.md or None if not found.
    """
    research_md = artifact_dir / "research.md"
    if research_md.exists():
        return research_md.read_text(encoding="utf-8")
    return None


def read_ticket_id_file(artifact_dir: Path) -> Optional[str]:
    """Read ticket_id.txt artifact if it exists.
    
    Args:
        artifact_dir: Path to the artifact directory.
        
    Returns:
        Ticket ID or None if not found.
    """
    ticket_id_file = artifact_dir / "ticket_id.txt"
    if ticket_id_file.exists():
        content = ticket_id_file.read_text(encoding="utf-8").strip()
        return content if content else None
    return None


def handle_retry_reset(artifact_dir: Path, ticket_id: str) -> bool:
    """Handle --retry-reset flag by renaming existing retry-state.json.
    
    Args:
        artifact_dir: Path to the artifact directory.
        ticket_id: Ticket ID for logging.
        
    Returns:
        True if reset was performed, False otherwise.
    """
    retry_state_path = artifact_dir / "retry-state.json"
    if not retry_state_path.exists():
        return False
    
    # Generate ISO 8601 timestamp with random suffix
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    random_suffix = secrets.token_hex(4)
    backup_name = f"retry-state.json.bak.{timestamp}.{random_suffix}"
    backup_path = artifact_dir / backup_name
    
    shutil.move(str(retry_state_path), str(backup_path))
    print(f"Retry state reset for {ticket_id}")
    print(f"  - Backed up to: {backup_name}")
    
    return True


def load_retry_state(artifact_dir: Path, ticket_id: str) -> RetryState:
    """Load or create retry state for the ticket.
    
    Args:
        artifact_dir: Path to the artifact directory.
        ticket_id: The ticket ID.
        
    Returns:
        RetryState instance.
    """
    state = RetryState.load(artifact_dir)
    if state is None:
        state = RetryState(artifact_dir, ticket_id=ticket_id)
        state.save()
    return state


def parse_ticket_frontmatter(ticket_content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from ticket content.
    
    Args:
        ticket_content: The ticket content.
        
    Returns:
        Dictionary with frontmatter fields.
    """
    result: dict[str, Any] = {}
    
    if not ticket_content.startswith("---"):
        return result
    
    # Find end of frontmatter
    parts = ticket_content.split("---", 2)
    if len(parts) < 3:
        return result
    
    frontmatter = parts[1].strip()
    
    # Simple YAML parsing for common fields
    for line in frontmatter.splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # Handle arrays
            if value.startswith("[") and value.endswith("]"):
                # Remove brackets and split by comma
                inner = value[1:-1]
                result[key] = [v.strip().strip('"\'') for v in inner.split(",") if v.strip()]
            else:
                result[key] = value
    
    return result


def extract_ticket_body(ticket_content: str) -> str:
    """Extract body from ticket content (without frontmatter).
    
    Args:
        ticket_content: The ticket content.
        
    Returns:
        The ticket body.
    """
    if not ticket_content.startswith("---"):
        return ticket_content
    
    parts = ticket_content.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    
    return ticket_content


def run_quality_checks(
    changed_files: list[str],
    project_root: Path,
    workflow_config: dict,
) -> dict[str, Any]:
    """Run quality checks on changed files.
    
    Args:
        changed_files: List of changed file paths.
        project_root: Path to the project root.
        workflow_config: Workflow configuration.
        
    Returns:
        Dictionary with check results.
    """
    results = {
        "lint": {"passed": True, "output": ""},
        "format": {"passed": True, "output": ""},
        "typecheck": {"passed": True, "output": ""},
    }
    
    checkers = workflow_config.get("checkers", {})
    if not checkers:
        return results
    
    # Group files by language
    files_by_lang: dict[str, list[str]] = {}
    for filepath in changed_files:
        for lang, config in checkers.items():
            pattern = config.get("files", "")
            if pattern and re.search(pattern, filepath):
                files_by_lang.setdefault(lang, []).append(filepath)
                break
    
    # Run checks per language
    for lang, files in files_by_lang.items():
        if lang not in checkers:
            continue
        
        config = checkers[lang]
        files_str = " ".join(shlex.quote(f) for f in files)
        
        # Run format
        if "format" in config:
            cmd = config["format"].format(files=files_str)
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=120,
                )
                if proc.returncode != 0:
                    results["format"]["passed"] = False
                    results["format"]["output"] += f"\n{lang}: {proc.stderr or proc.stdout}"
            except Exception as e:
                results["format"]["passed"] = False
                results["format"]["output"] += f"\n{lang}: Error running format: {e}"
        
        # Run lint
        if "lint" in config:
            cmd = config["lint"].format(files=files_str)
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=120,
                )
                if proc.returncode != 0:
                    results["lint"]["passed"] = False
                    results["lint"]["output"] += f"\n{lang}: {proc.stderr or proc.stdout}"
            except Exception as e:
                results["lint"]["passed"] = False
                results["lint"]["output"] += f"\n{lang}: Error running lint: {e}"
    
    # Run typecheck on project (not per-file)
    # Use the first language with typecheck command
    for lang, config in checkers.items():
        if "typecheck" in config:
            cmd = config["typecheck"]
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=300,
                )
                if proc.returncode != 0:
                    results["typecheck"]["passed"] = False
                    results["typecheck"]["output"] += f"\n{lang}: {proc.stderr or proc.stdout}"
            except Exception as e:
                results["typecheck"]["passed"] = False
                results["typecheck"]["output"] += f"\n{lang}: Error running typecheck: {e}"
            break  # Only run typecheck once
    
    return results


def run_tests(project_root: Path) -> dict[str, Any]:
    """Run tests for the project.
    
    Args:
        project_root: Path to the project root.
        
    Returns:
        Dictionary with test results.
    """
    results = {
        "run": False,
        "passed": True,
        "output": "",
        "command": "",
    }
    
    # Detect test framework and run tests
    test_commands = [
        # Python
        ("pytest", ["pytest", "-v"]),
        ("python -m pytest", ["python", "-m", "pytest", "-v"]),
        # JavaScript/TypeScript
        ("npm test", ["npm", "test"]),
        # Rust
        ("cargo test", ["cargo", "test"]),
        # Go
        ("go test", ["go", "test", "./..."]),
    ]
    
    for name, cmd in test_commands:
        executable = shutil.which(cmd[0])
        if executable:
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
                results["output"] = proc.stdout + "\n" + proc.stderr
                results["command"] = " ".join(cmd)
                break
            except Exception as e:
                results["run"] = True
                results["passed"] = False
                results["output"] = f"Error running tests: {e}"
                results["command"] = " ".join(cmd)
                break
    
    return results


def write_implementation_md(
    artifact_dir: Path,
    ticket_id: str,
    ticket_content: str,
    changed_files: list[str],
    attempt_number: int,
    escalated_models: dict[str, str | None],
    quality_results: dict[str, Any],
    test_results: dict[str, Any],
) -> Path:
    """Write implementation.md artifact.
    
    Args:
        artifact_dir: Directory to write the artifact.
        ticket_id: The ticket ID.
        ticket_content: The ticket content.
        changed_files: List of changed file paths.
        attempt_number: Current attempt number.
        escalated_models: Dictionary of escalated models.
        quality_results: Quality check results.
        test_results: Test results.
        
    Returns:
        Path to the written file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract ticket body for summary
    ticket_body = extract_ticket_body(ticket_content)
    
    # Get first line of body as summary
    summary = ticket_body.splitlines()[0] if ticket_body else "Implementation"
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    lines = [
        f"# Implementation: {ticket_id}",
        "",
        "## Summary",
        summary,
        "",
        "## Retry Context",
        f"- Attempt: {attempt_number}",
        f"- Escalated Models: fixer={escalated_models.get('fixer') or 'base'}, "
        f"reviewer-second={escalated_models.get('reviewerSecondOpinion') or 'base'}, "
        f"worker={escalated_models.get('worker') or 'base'}",
        "",
        "## Files Changed",
    ]
    
    if changed_files:
        for filepath in changed_files:
            lines.append(f"- `{filepath}`")
    else:
        lines.append("- No files changed")
    
    lines.extend([
        "",
        "## Key Decisions",
        "- Implementation follows existing project patterns",
    ])
    
    # Add quality check results
    lines.extend([
        "",
        "## Quality Checks",
    ])
    
    if quality_results["lint"]["passed"]:
        lines.append("- ✅ Lint: Passed")
    else:
        lines.append("- ❌ Lint: Failed")
        if quality_results["lint"]["output"]:
            lines.append(f"  ```\n{quality_results['lint']['output'][:500]}\n  ```")
    
    if quality_results["format"]["passed"]:
        lines.append("- ✅ Format: Passed")
    else:
        lines.append("- ❌ Format: Failed")
        if quality_results["format"]["output"]:
            lines.append(f"  ```\n{quality_results['format']['output'][:500]}\n  ```")
    
    if quality_results["typecheck"]["passed"]:
        lines.append("- ✅ Typecheck: Passed")
    else:
        lines.append("- ❌ Typecheck: Failed")
        if quality_results["typecheck"]["output"]:
            lines.append(f"  ```\n{quality_results['typecheck']['output'][:500]}\n  ```")
    
    # Add test results
    lines.extend([
        "",
        "## Tests Run",
    ])
    
    if test_results["run"]:
        if test_results["passed"]:
            lines.append(f"- ✅ Tests passed ({test_results['command']})")
        else:
            lines.append(f"- ❌ Tests failed ({test_results['command']})")
            if test_results["output"]:
                lines.append(f"  ```\n{test_results['output'][:500]}\n  ```")
    else:
        lines.append("- No tests detected or run")
    
    lines.extend([
        "",
        "## Verification",
        "- Review the changes in the Files Changed section above",
        "- Run quality checks locally if needed",
        "- Verify tests pass before proceeding to review phase",
    ])
    
    implementation_md = artifact_dir / "implementation.md"
    implementation_md.write_text("\n".join(lines), encoding="utf-8")
    
    return implementation_md


def write_ticket_id_file(artifact_dir: Path, ticket_id: str) -> Path:
    """Write ticket_id.txt artifact for chain preservation.
    
    Args:
        artifact_dir: Directory to write the artifact.
        ticket_id: The ticket ID.
        
    Returns:
        Path to the written file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    ticket_id_file = artifact_dir / "ticket_id.txt"
    ticket_id_file.write_text(ticket_id + "\n", encoding="utf-8")
    return ticket_id_file


def write_files_changed(
    artifact_dir: Path,
    changed_files: list[str],
) -> Path:
    """Write files_changed.txt artifact atomically.
    
    Args:
        artifact_dir: Directory to write the artifact.
        changed_files: List of changed file paths.
        
    Returns:
        Path to the written file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file first, then rename for atomicity
    files_changed_path = artifact_dir / "files_changed.txt"
    temp_path = files_changed_path.with_suffix(".tmp")
    
    content = "\n".join(changed_files) + "\n" if changed_files else ""
    temp_path.write_text(content, encoding="utf-8")
    
    # Atomic rename
    os.replace(str(temp_path), str(files_changed_path))
    
    return files_changed_path


def resolve_escalated_models(
    retry_state: RetryState,
    workflow_config: dict,
) -> dict[str, str | None]:
    """Resolve escalated models based on retry state.
    
    Args:
        retry_state: The retry state.
        workflow_config: Workflow configuration.
        
    Returns:
        Dictionary with escalated model IDs.
    """
    escalation_config = workflow_config.get("escalation", {})
    
    # Base models from agents config
    agents_config = workflow_config.get("agents", {})
    base_models = {
        "fixer": agents_config.get("fixer"),
        "reviewerSecondOpinion": agents_config.get("reviewer-second-opinion"),
        "worker": agents_config.get("worker"),
    }
    
    # Get next attempt number
    attempt_number = retry_state.get_attempt_number() + 1
    
    # Check if last attempt was blocked
    if retry_state.is_blocked():
        # Increment for blocked retry
        attempt_number = retry_state.get_attempt_number() + 1
    
    escalated = retry_state.resolve_escalation(
        escalation_config,
        base_models,
        next_attempt_number=attempt_number,
    )
    
    return {
        "fixer": escalated.fixer,
        "reviewerSecondOpinion": escalated.reviewerSecondOpinion,
        "worker": escalated.worker,
    }


def explore_codebase(
    project_root: Path,
    ticket_content: str,
) -> list[str]:
    """Explore codebase to find relevant files.
    
    Args:
        project_root: Path to the project root.
        ticket_content: The ticket content.
        
    Returns:
        List of relevant file paths.
    """
    relevant_files: list[str] = []
    
    # Extract keywords from ticket
    body = extract_ticket_body(ticket_content)
    
    # Look for file mentions in ticket
    file_patterns = [
        r"`([^`]+\.(py|ts|js|rs|go|java|kt|swift|c|cpp|h|hpp|rb|php))`",
        r"\b([a-zA-Z_][a-zA-Z0-9_]*\.(py|ts|js|rs|go))\b",
    ]
    
    mentioned_files: set[str] = set()
    for pattern in file_patterns:
        for match in re.finditer(pattern, body, re.IGNORECASE):
            mentioned_files.add(match.group(1))
    
    # Check if mentioned files exist
    for filename in mentioned_files:
        filepath = project_root / filename
        if filepath.exists():
            relevant_files.append(str(filepath.relative_to(project_root)))
    
    return relevant_files


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for tf-implement command.
    
    Args:
        argv: Command line arguments.
        
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        prog="tf-implement",
        description="Execute the Implementation phase for TF workflow ticket implementation.",
    )
    parser.add_argument(
        "ticket_id",
        help="The ticket to implement (e.g., pt-1234)",
    )
    parser.add_argument(
        "--retry-reset",
        dest="retry_reset",
        action="store_true",
        help="Force a fresh retry attempt (renames existing retry-state.json)",
    )
    
    args = parser.parse_args(argv)
    
    # Find project root
    project_root = find_project_root()
    if project_root is None:
        print("Error: Could not find project root (no .tf or .pi directory)", file=sys.stderr)
        return 1
    
    # Load workflow configuration
    workflow_config = load_workflow_config(project_root)
    knowledge_dir_path = workflow_config.get("knowledgeDir", ".tf/knowledge")
    
    # Resolve knowledge directory
    knowledge_dir = Path(knowledge_dir_path)
    if not knowledge_dir.is_absolute():
        knowledge_dir = project_root / knowledge_dir
    
    # Prepare artifact directory
    artifact_dir = knowledge_dir / "tickets" / args.ticket_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Implementation phase for ticket: {args.ticket_id}")
    print(f"Project root: {project_root}")
    print(f"Artifact dir: {artifact_dir}")
    
    # Step 1: Re-Anchor Context
    print("\n[Step 1] Re-anchoring context...")
    
    # Read AGENTS.md files
    root_agents = read_agents_md(project_root)
    if root_agents:
        print("  - Read root AGENTS.md")
    
    ralph_agents = read_ralph_agents_md(project_root)
    if ralph_agents:
        print("  - Read .tf/ralph/AGENTS.md")
    
    # Handle retry reset
    if args.retry_reset:
        if handle_retry_reset(artifact_dir, args.ticket_id):
            pass  # Already logged
    
    # Load retry state
    retry_state = load_retry_state(artifact_dir, args.ticket_id)
    attempt_number = retry_state.get_attempt_number() + 1
    print(f"  - Attempt number: {attempt_number}")
    
    # Resolve escalated models
    escalated_models = resolve_escalated_models(retry_state, workflow_config)
    if any(escalated_models.values()):
        print(f"  - Escalated models: {escalated_models}")
    
    # Read research.md
    research_content = read_research_md(artifact_dir)
    if research_content:
        print("  - Read research.md")
    
    # Read existing ticket_id.txt
    existing_ticket_id = read_ticket_id_file(artifact_dir)
    if existing_ticket_id and existing_ticket_id != args.ticket_id:
        print(f"  - Warning: ticket_id.txt contains {existing_ticket_id}, overwriting with {args.ticket_id}")
    
    # Get ticket details
    try:
        ticket_content = run_tk_show(args.ticket_id)
        print(f"  - Retrieved ticket: {args.ticket_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get ticket {args.ticket_id}: {e}", file=sys.stderr)
        return 1
    
    # Parse ticket frontmatter
    frontmatter = parse_ticket_frontmatter(ticket_content)
    ticket_type = frontmatter.get("type", "unknown")
    ticket_status = frontmatter.get("status", "unknown")
    print(f"  - Ticket type: {ticket_type}, status: {ticket_status}")
    
    # Step 2: Explore Codebase
    print("\n[Step 2] Exploring codebase...")
    relevant_files = explore_codebase(project_root, ticket_content)
    if relevant_files:
        print(f"  - Found {len(relevant_files)} potentially relevant files:")
        for f in relevant_files[:5]:
            print(f"    - {f}")
        if len(relevant_files) > 5:
            print(f"    ... and {len(relevant_files) - 5} more")
    else:
        print("  - No specific files mentioned in ticket")
    
    # Step 3: Implement Changes
    print("\n[Step 3] Implementing changes...")
    print("  - This phase is executed by the AI agent")
    print("  - The agent should make focused, single-responsibility changes")
    print("  - Changed files will be tracked automatically")
    
    # Track changed files (in-memory for now - will be populated by AI)
    changed_files: list[str] = []
    
    # Note: The actual implementation is done by the AI agent
    # This command provides the framework and context
    
    # Step 4: Run Quality Checks
    print("\n[Step 4] Running quality checks...")
    
    # Get changed files from git or track file
    files_changed_path = artifact_dir / "files_changed.txt"
    if files_changed_path.exists():
        content = files_changed_path.read_text(encoding="utf-8")
        changed_files = [line.strip() for line in content.splitlines() if line.strip()]
    
    if changed_files:
        print(f"  - Checking {len(changed_files)} changed files...")
        quality_results = run_quality_checks(changed_files, project_root, workflow_config)
        
        if quality_results["lint"]["passed"]:
            print("  - ✅ Lint passed")
        else:
            print("  - ❌ Lint failed (see implementation.md for details)")
        
        if quality_results["format"]["passed"]:
            print("  - ✅ Format passed")
        else:
            print("  - ❌ Format failed (see implementation.md for details)")
        
        if quality_results["typecheck"]["passed"]:
            print("  - ✅ Typecheck passed")
        else:
            print("  - ⚠️ Typecheck issues (see implementation.md for details)")
    else:
        print("  - No changed files to check")
        quality_results = {
            "lint": {"passed": True, "output": ""},
            "format": {"passed": True, "output": ""},
            "typecheck": {"passed": True, "output": ""},
        }
    
    # Step 5: Run Tests
    print("\n[Step 5] Running tests...")
    test_results = run_tests(project_root)
    
    if test_results["run"]:
        if test_results["passed"]:
            print(f"  - ✅ Tests passed ({test_results['command']})")
        else:
            print(f"  - ⚠️ Tests failed ({test_results['command']})")
            print("    (Failures documented in implementation.md)")
    else:
        print("  - No tests detected")
    
    # Step 6: Write implementation.md
    print("\n[Step 6] Writing implementation artifact...")
    
    implementation_path = write_implementation_md(
        artifact_dir,
        args.ticket_id,
        ticket_content,
        changed_files,
        attempt_number,
        escalated_models,
        quality_results,
        test_results,
    )
    print(f"  - Written: {implementation_path}")
    
    # Step 7: Write artifacts
    print("\n[Step 7] Writing artifact files...")
    
    # Always write ticket_id.txt
    write_ticket_id_file(artifact_dir, args.ticket_id)
    print(f"  - Written: ticket_id.txt")
    
    # Write files_changed.txt (even if empty - creates the file)
    write_files_changed(artifact_dir, changed_files)
    print(f"  - Written: files_changed.txt ({len(changed_files)} files)")
    
    # Update retry state to mark attempt started
    retry_state.start_attempt(trigger="implementation")
    retry_state.save()
    
    # Summary
    print("\n" + "=" * 50)
    print("Implementation phase complete!")
    print(f"Ticket: {args.ticket_id}")
    print(f"Artifact directory: {artifact_dir}")
    print(f"Attempt: {attempt_number}")
    print(f"Files changed: {len(changed_files)}")
    print("")
    print("Next steps:")
    print("  1. Review implementation.md for details")
    print("  2. Proceed to review phase: /tf-review")
    print("")
    print("Note: Actual code changes should be made by the AI agent")
    print("      during this phase. Use 'tf track <file>' to add files.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
