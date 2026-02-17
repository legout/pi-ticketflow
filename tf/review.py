"""Review phase command for TF workflow.

Implements the /tf-review command which executes the Review phase
for ticket implementation according to the tf-workflow specification.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Optional

from tf.retry_state import RetryState
from tf.utils import find_project_root


DEFAULT_REVIEWERS = [
    "reviewer-general",
    "reviewer-spec-audit",
    "reviewer-second-opinion",
]

REVIEWER_OUTPUTS = {
    "reviewer-general": "review-general.md",
    "reviewer-spec-audit": "review-spec.md",
    "reviewer-second-opinion": "review-second.md",
}

REVIEWER_LENSES = {
    "reviewer-general": "general",
    "reviewer-spec-audit": "spec-audit",
    "reviewer-second-opinion": "second-opinion",
}

SEVERITY_ORDER = {
    "Critical": 0,
    "Major": 1,
    "Minor": 2,
    "Warnings": 3,
    "Suggestions": 4,
}

SEVERITY_TITLES = {
    "Critical": "## Critical (must fix)",
    "Major": "## Major (should fix)",
    "Minor": "## Minor (nice to fix)",
    "Warnings": "## Warnings (follow-up ticket)",
    "Suggestions": "## Suggestions (follow-up ticket)",
}


@dataclass
class ReviewerRunResult:
    reviewer: str
    success: bool
    output_path: Path
    error: str = ""


@dataclass
class Issue:
    severity: str
    location: str
    description: str
    sources: set[str] = field(default_factory=set)


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


def resolve_repo_root(cwd: Path) -> Path:
    """Resolve repository root via git rev-parse, fallback to cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        out = result.stdout.strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return cwd


def resolve_reviewers(settings: dict[str, Any]) -> list[str]:
    """Resolve reviewer list from config with defaults."""
    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    configured = workflow.get("enableReviewers")

    if isinstance(configured, list):
        return [r for r in configured if isinstance(r, str) and r.strip()]

    return list(DEFAULT_REVIEWERS)


def resolve_escalated_models(
    artifact_dir: Path,
    settings: dict[str, Any],
) -> dict[str, str | None]:
    """Resolve escalated models from retry-state for current attempt.

    Only reviewerSecondOpinion is used in this phase, but we keep the full shape
    for consistency with other phases.

    Attempt semantics:
    - If the last attempt is BLOCKED and no new attempt started yet, use next attempt.
    - Otherwise, use the current attempt number (review runs within the active attempt).
    """
    state = RetryState.load(artifact_dir)
    if state is None:
        return {
            "fixer": None,
            "reviewerSecondOpinion": None,
            "worker": None,
        }

    workflow = settings.get("workflow", {}) if isinstance(settings, dict) else {}
    escalation_cfg = workflow.get("escalation", {}) if isinstance(workflow, dict) else {}

    # Resolve base reviewer-second-opinion model.
    base_reviewer_second = resolve_reviewer_model(
        reviewer="reviewer-second-opinion",
        settings=settings,
        escalated_models={
            "fixer": None,
            "reviewerSecondOpinion": None,
            "worker": None,
        },
    )[0]

    base_models = {
        "fixer": None,
        "reviewerSecondOpinion": base_reviewer_second,
        "worker": None,
    }

    state_data = state.to_dict()
    attempts = state_data.get("attempts", [])
    if not attempts:
        effective_attempt_number = 1
    else:
        last_status = attempts[-1].get("status")
        if last_status == "blocked":
            effective_attempt_number = state.get_attempt_number() + 1
        else:
            effective_attempt_number = max(1, state.get_attempt_number())

    escalated = state.resolve_escalation(
        escalation_cfg,
        base_models,
        next_attempt_number=effective_attempt_number,
    )

    return {
        "fixer": escalated.fixer,
        "reviewerSecondOpinion": escalated.reviewerSecondOpinion,
        "worker": escalated.worker,
    }


def resolve_reviewer_model(
    reviewer: str,
    settings: dict[str, Any],
    escalated_models: dict[str, str | None],
) -> tuple[str | None, str | None]:
    """Resolve reviewer model and thinking from config.

    Resolution order:
    1) Escalation override for reviewer-second-opinion
    2) agents.<reviewer> -> metaModels.<key>.model
    3) If agents.<reviewer> looks like direct model id, use it directly
    4) Fallback to hardcoded defaults
    """
    # Escalation override for second opinion reviewer
    if reviewer == "reviewer-second-opinion":
        escalated = escalated_models.get("reviewerSecondOpinion")
        if escalated:
            # Keep thinking from configured meta-model if available.
            _, thinking = _resolve_model_from_agents_map(reviewer, settings)
            return escalated, thinking

    model, thinking = _resolve_model_from_agents_map(reviewer, settings)
    if model:
        return model, thinking

    defaults = {
        "reviewer-general": ("openai-codex/gpt-5.3-codex", "high"),
        "reviewer-spec-audit": ("openai-codex/gpt-5.1-codex-mini", "high"),
        "reviewer-second-opinion": ("kimi-coding/k2p5", "high"),
    }
    return defaults.get(reviewer, (None, None))


def _resolve_model_from_agents_map(
    reviewer: str,
    settings: dict[str, Any],
) -> tuple[str | None, str | None]:
    agents = settings.get("agents", {}) if isinstance(settings, dict) else {}
    meta_models = settings.get("metaModels", {}) if isinstance(settings, dict) else {}

    mapped = agents.get(reviewer)
    if not mapped:
        return None, None

    # Meta-model key path
    if isinstance(mapped, str) and isinstance(meta_models.get(mapped), dict):
        mm = meta_models[mapped]
        model = mm.get("model")
        thinking = mm.get("thinking")
        if isinstance(model, str):
            return model, thinking if isinstance(thinking, str) else None

    # Direct model id path
    if isinstance(mapped, str) and "/" in mapped:
        return mapped, None

    return None, None


def _reviewer_prompt(
    reviewer: str,
    ticket_id: str,
    artifact_dir: Path,
    output_path: Path,
) -> str:
    lens = REVIEWER_LENSES.get(reviewer, "general")
    implementation = artifact_dir / "implementation.md"
    files_changed = artifact_dir / "files_changed.txt"

    return (
        f"Review ticket {ticket_id} with lens '{lens}'.\\n"
        f"Required context files:\\n"
        f"- {implementation}\\n"
        f"- {files_changed} (if present)\\n\\n"
        "You must:\\n"
        "1) Read implementation context and referenced files.\\n"
        "2) Report concrete findings with path:line references where possible.\\n"
        "3) Write final review markdown to this exact file path:\\n"
        f"   {output_path}\\n\\n"
        "Use this structure:\\n"
        f"# Review: {ticket_id}\\n"
        "## Overall Assessment\\n"
        "2-3 sentence summary.\\n\\n"
        "## Critical (must fix)\\n"
        "- `path:line` - issue\\n\\n"
        "## Major (should fix)\\n"
        "- ...\\n\\n"
        "## Minor (nice to fix)\\n"
        "- ...\\n\\n"
        "## Warnings (follow-up ticket)\\n"
        "- ...\\n\\n"
        "## Suggestions (follow-up ticket)\\n"
        "- ...\\n\\n"
        "## Summary Statistics\\n"
        "- Critical: {count}\\n"
        "- Major: {count}\\n"
        "- Minor: {count}\\n"
        "- Warnings: {count}\\n"
        "- Suggestions: {count}\\n"
    )


def run_parallel_subagents(
    reviewers: list[str],
    ticket_id: str,
    repo_root: Path,
    model_overrides: dict[str, str | None],
    timeout_seconds: int = 330,
) -> tuple[bool, str]:
    """Run reviewer fan-out via pi-subagents /parallel command.

    Returns:
        (success, error_message)
    """
    if not reviewers:
        return True, ""

    steps: list[str] = []
    task = ticket_id.replace('"', '\\"')

    for reviewer in reviewers:
        agent_spec = reviewer
        model = model_overrides.get(reviewer)
        if model:
            # Slash command supports inline per-step config: agent[key=value]
            agent_spec = f"{reviewer}[model={model}]"
        steps.append(f'{agent_spec} "{task}"')

    prompt = "/parallel " + " -> ".join(steps)

    cmd = ["pi", "--no-session", "-p", prompt]

    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return False, f"Parallel reviewer run timed out after {timeout_seconds}s"
    except Exception as exc:
        return False, f"Parallel reviewer run failed: {exc}"

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "parallel run failed").strip()
        return False, err[-1000:]

    return True, ""


def run_reviewer(
    reviewer: str,
    ticket_id: str,
    artifact_dir: Path,
    repo_root: Path,
    model: str | None,
    thinking: str | None,
    timeout_seconds: int = 300,
) -> ReviewerRunResult:
    """Run one reviewer using a dedicated pi process (fallback mode)."""
    output_name = REVIEWER_OUTPUTS.get(reviewer, f"{reviewer}.md")
    output_path = artifact_dir / output_name

    prompt = _reviewer_prompt(reviewer, ticket_id, artifact_dir, output_path)

    cmd = ["pi", "--no-session"]
    if model:
        cmd.extend(["--model", model])
    if thinking:
        cmd.extend(["--thinking", thinking])
    cmd.extend(["-p", prompt])

    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return ReviewerRunResult(
            reviewer=reviewer,
            success=False,
            output_path=output_path,
            error=f"Timed out after {timeout_seconds}s",
        )
    except Exception as exc:
        return ReviewerRunResult(
            reviewer=reviewer,
            success=False,
            output_path=output_path,
            error=f"Execution failed: {exc}",
        )

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "pi exited non-zero").strip()
        return ReviewerRunResult(
            reviewer=reviewer,
            success=False,
            output_path=output_path,
            error=err[-500:],
        )

    if not output_path.exists() or not output_path.read_text(encoding="utf-8").strip():
        return ReviewerRunResult(
            reviewer=reviewer,
            success=False,
            output_path=output_path,
            error="No review output generated",
        )

    return ReviewerRunResult(
        reviewer=reviewer,
        success=True,
        output_path=output_path,
    )


def run_reviewers_fallback(
    reviewers: list[str],
    ticket_id: str,
    artifact_dir: Path,
    repo_root: Path,
    reviewer_models: dict[str, str | None],
    reviewer_thinking: dict[str, str | None],
    timeout_seconds: int = 300,
) -> list[ReviewerRunResult]:
    """Run reviewers in parallel as individual pi processes.

    This is used when /parallel fails, or when /parallel returns without
    producing expected reviewer output files.
    """
    if not reviewers:
        return []

    results: list[ReviewerRunResult] = []
    with ThreadPoolExecutor(max_workers=max(1, len(reviewers))) as executor:
        futures = {}
        for reviewer in reviewers:
            futures[
                executor.submit(
                    run_reviewer,
                    reviewer,
                    ticket_id,
                    artifact_dir,
                    repo_root,
                    reviewer_models.get(reviewer),
                    reviewer_thinking.get(reviewer),
                    timeout_seconds,
                )
            ] = reviewer

        for future in as_completed(futures):
            reviewer = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # defensive
                output_path = artifact_dir / REVIEWER_OUTPUTS.get(reviewer, f"{reviewer}.md")
                results.append(
                    ReviewerRunResult(
                        reviewer=reviewer,
                        success=False,
                        output_path=output_path,
                        error=f"Unhandled exception: {exc}",
                    )
                )

    return results


def write_failed_reviewer_stub(
    output_path: Path,
    ticket_id: str,
    reviewer: str,
    reason: str,
) -> None:
    """Write partial review stub for failed reviewers."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            f"# Review: {ticket_id}",
            "",
            "## Overall Assessment",
            f"Reviewer `{reviewer}` failed. Stub created by tf review phase.",
            "",
            "## Critical (must fix)",
            f"- Review failed: {reason}",
            "",
            "## Major (should fix)",
            "None",
            "",
            "## Minor (nice to fix)",
            "None",
            "",
            "## Warnings (follow-up ticket)",
            "None",
            "",
            "## Suggestions (follow-up ticket)",
            "None",
            "",
            "## Summary Statistics",
            "- Critical: 1",
            "- Major: 0",
            "- Minor: 0",
            "- Warnings: 0",
            "- Suggestions: 0",
            "",
        ]
    )
    output_path.write_text(content, encoding="utf-8")


def parse_review_issues(content: str, source: str) -> list[Issue]:
    """Parse issues from a reviewer markdown output."""
    issues: list[Issue] = []

    section_for_line: str | None = None
    section_regexes = {
        "Critical": re.compile(r"^##\s*Critical\b", re.IGNORECASE),
        "Major": re.compile(r"^##\s*Major\b", re.IGNORECASE),
        "Minor": re.compile(r"^##\s*Minor\b", re.IGNORECASE),
        "Warnings": re.compile(r"^##\s*Warnings\b", re.IGNORECASE),
        "Suggestions": re.compile(r"^##\s*Suggestions\b", re.IGNORECASE),
    }

    for raw in content.splitlines():
        line = raw.rstrip()

        matched_section = None
        for sev, pattern in section_regexes.items():
            if pattern.match(line):
                matched_section = sev
                break

        if matched_section is not None:
            section_for_line = matched_section
            continue

        if line.startswith("## "):
            section_for_line = None
            continue

        if section_for_line not in SEVERITY_ORDER:
            continue

        stripped = line.strip()
        if not stripped.startswith("-"):
            continue

        bullet = stripped.lstrip("-").strip()
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
                sources={source},
            )
        )

    return issues


def _split_location_and_description(bullet: str) -> tuple[str, str]:
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


def deduplicate_issues(issues: list[Issue]) -> list[Issue]:
    """Deduplicate issues by location + fuzzy description similarity.

    Duplicate criteria:
    - same normalized location
    - description similarity > 0.70
    """
    merged: list[Issue] = []

    for issue in issues:
        duplicate_idx = None
        for idx, existing in enumerate(merged):
            if _is_duplicate(existing, issue):
                duplicate_idx = idx
                break

        if duplicate_idx is None:
            merged.append(issue)
            continue

        existing = merged[duplicate_idx]
        existing.sources.update(issue.sources)

        # Keep highest severity (lower numeric rank is higher severity)
        if SEVERITY_ORDER[issue.severity] < SEVERITY_ORDER[existing.severity]:
            existing.severity = issue.severity
            existing.description = issue.description
            existing.location = issue.location

    return merged


def _is_duplicate(a: Issue, b: Issue) -> bool:
    loc_a = _normalize_location(a.location)
    loc_b = _normalize_location(b.location)
    if loc_a != loc_b:
        return False

    similarity = SequenceMatcher(None, a.description.lower(), b.description.lower()).ratio()
    return similarity >= 0.70


def _normalize_location(location: str) -> str:
    return re.sub(r"\s+", "", location.strip().lower())


def build_consolidated_review(ticket_id: str, issues: list[Issue]) -> str:
    grouped: dict[str, list[Issue]] = {
        "Critical": [],
        "Major": [],
        "Minor": [],
        "Warnings": [],
        "Suggestions": [],
    }

    for issue in issues:
        if issue.severity in grouped:
            grouped[issue.severity].append(issue)

    # Stable sort within severity
    for severity in grouped:
        grouped[severity].sort(key=lambda i: (_normalize_location(i.location), i.description.lower()))

    lines: list[str] = [
        f"# Review: {ticket_id}",
        "",
    ]

    no_issues = all(len(grouped[s]) == 0 for s in grouped)

    for severity in ["Critical", "Major", "Minor", "Warnings", "Suggestions"]:
        lines.append(SEVERITY_TITLES[severity])
        if no_issues and severity == "Critical":
            lines.append("No issues found")
            lines.append("")
            continue

        if not grouped[severity]:
            lines.append("None")
            lines.append("")
            continue

        for issue in grouped[severity]:
            sources = ", ".join(sorted(issue.sources))
            lines.append(f"- `{issue.location}` - {issue.description} _(sources: {sources})_")
        lines.append("")

    lines.extend(
        [
            "## Summary Statistics",
            f"- Critical: {len(grouped['Critical'])}",
            f"- Major: {len(grouped['Major'])}",
            f"- Minor: {len(grouped['Minor'])}",
            f"- Warnings: {len(grouped['Warnings'])}",
            f"- Suggestions: {len(grouped['Suggestions'])}",
            "",
        ]
    )

    return "\n".join(lines)


def build_no_reviews_stub(ticket_id: str) -> str:
    return "\n".join(
        [
            f"# Review: {ticket_id}",
            "",
            "## Critical (must fix)",
            "No reviews run",
            "",
            "## Major (should fix)",
            "None",
            "",
            "## Minor (nice to fix)",
            "None",
            "",
            "## Warnings (follow-up ticket)",
            "None",
            "",
            "## Suggestions (follow-up ticket)",
            "None",
            "",
            "## Summary Statistics",
            "- Critical: 0",
            "- Major: 0",
            "- Minor: 0",
            "- Warnings: 0",
            "- Suggestions: 0",
            "",
        ]
    )


def main(argv: Optional[list[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="tf-review",
        description="Execute the Review phase for TF workflow ticket implementation.",
    )
    parser.add_argument("ticket_id", help="The ticket to review (e.g., pt-1234)")
    args = parser.parse_args(argv)

    project_root = find_project_root()
    if project_root is None:
        print("Error: Could not find project root (no .tf or .pi directory)", file=sys.stderr)
        return 1

    settings = load_settings(project_root)

    # Step 1: Re-anchor context
    print(f"Review phase for ticket: {args.ticket_id}")
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

    implementation_md = artifact_dir / "implementation.md"
    if implementation_md.exists():
        print("  - Found implementation.md")
    else:
        print("  - Warning: implementation.md not found")

    escalated_models = resolve_escalated_models(artifact_dir, settings)
    if escalated_models.get("reviewerSecondOpinion"):
        print(
            "  - Escalated reviewer-second-opinion model: "
            f"{escalated_models['reviewerSecondOpinion']}"
        )

    try:
        _ = run_tk_show(args.ticket_id, cwd=project_root)
        print(f"  - Retrieved ticket details: tk show {args.ticket_id}")
    except subprocess.CalledProcessError as exc:
        print(f"Error: Failed to get ticket {args.ticket_id}: {exc}", file=sys.stderr)
        return 1

    # Step 2: Determine reviewers
    print("\n[Step 2] Determining reviewers...")
    reviewers = resolve_reviewers(settings)
    if reviewers:
        print(f"  - Reviewers: {', '.join(reviewers)}")
    else:
        print("  - Reviews disabled via config (empty enableReviewers)")

    # Step 3: Resolve repo root
    print("\n[Step 3] Resolving repo root...")
    repo_root = resolve_repo_root(project_root)
    print(f"  - Repo root: {repo_root}")

    # Step 4/5: Execute reviewers (best-effort) or write no-review stub
    print("\n[Step 4] Executing reviewer fan-out...")

    if not reviewers:
        review_md = artifact_dir / "review.md"
        review_md.write_text(build_no_reviews_stub(args.ticket_id), encoding="utf-8")
        print(f"  - Wrote stub review: {review_md}")
        return 0

    reviewer_models: dict[str, str | None] = {}
    reviewer_thinking: dict[str, str | None] = {}
    for reviewer in reviewers:
        model, thinking = resolve_reviewer_model(reviewer, settings, escalated_models)
        reviewer_models[reviewer] = model
        reviewer_thinking[reviewer] = thinking

    parallel_ok, parallel_error = run_parallel_subagents(
        reviewers=reviewers,
        ticket_id=args.ticket_id,
        repo_root=repo_root,
        model_overrides=reviewer_models,
        timeout_seconds=330,
    )

    run_results_by_reviewer: dict[str, ReviewerRunResult] = {}

    if parallel_ok:
        print("  - Ran reviewer fan-out via /parallel")
        missing_after_parallel: list[str] = []
        for reviewer in reviewers:
            output_path = artifact_dir / REVIEWER_OUTPUTS.get(reviewer, f"{reviewer}.md")
            exists = output_path.exists() and output_path.read_text(encoding="utf-8").strip()
            result = ReviewerRunResult(
                reviewer=reviewer,
                success=bool(exists),
                output_path=output_path,
                error="" if exists else "Review failed or output missing after /parallel run",
            )
            run_results_by_reviewer[reviewer] = result
            if not result.success:
                missing_after_parallel.append(reviewer)

        # /parallel can succeed but still fail to produce reviewer files.
        # Retry only missing reviewers as individual subprocesses.
        if missing_after_parallel:
            print(
                "  - Missing reviewer outputs after /parallel; "
                f"retrying individually: {', '.join(missing_after_parallel)}"
            )
            fallback_results = run_reviewers_fallback(
                reviewers=missing_after_parallel,
                ticket_id=args.ticket_id,
                artifact_dir=artifact_dir,
                repo_root=repo_root,
                reviewer_models=reviewer_models,
                reviewer_thinking=reviewer_thinking,
                timeout_seconds=300,
            )
            for result in fallback_results:
                run_results_by_reviewer[result.reviewer] = result
    else:
        print(f"  - /parallel failed, falling back to per-reviewer execution: {parallel_error}")
        fallback_results = run_reviewers_fallback(
            reviewers=reviewers,
            ticket_id=args.ticket_id,
            artifact_dir=artifact_dir,
            repo_root=repo_root,
            reviewer_models=reviewer_models,
            reviewer_thinking=reviewer_thinking,
            timeout_seconds=300,
        )
        for result in fallback_results:
            run_results_by_reviewer[result.reviewer] = result

    run_results = [
        run_results_by_reviewer.get(
            reviewer,
            ReviewerRunResult(
                reviewer=reviewer,
                success=False,
                output_path=artifact_dir / REVIEWER_OUTPUTS.get(reviewer, f"{reviewer}.md"),
                error="Reviewer result missing",
            ),
        )
        for reviewer in reviewers
    ]

    for result in sorted(run_results, key=lambda r: r.reviewer):
        if result.success:
            print(f"  - ✅ {result.reviewer}: {result.output_path.name}")
        else:
            print(f"  - ⚠️ {result.reviewer} failed: {result.error}")
            write_failed_reviewer_stub(
                output_path=result.output_path,
                ticket_id=args.ticket_id,
                reviewer=result.reviewer,
                reason=result.error or "unknown failure",
            )
            print(f"    Wrote failure stub: {result.output_path.name}")

    # Step 5: Handle skipped reviews (no outputs at all)
    expected_paths = [r.output_path for r in run_results]
    existing_outputs = [p for p in expected_paths if p.exists() and p.read_text(encoding="utf-8").strip()]

    if not existing_outputs:
        print("\n[Step 5] No reviewer outputs found; writing stub consolidated review...")
        review_md = artifact_dir / "review.md"
        review_md.write_text(build_no_reviews_stub(args.ticket_id), encoding="utf-8")
        print(f"  - Written: {review_md}")
        return 0

    # Step 6: Merge reviews
    print("\n[Step 6] Merging reviews...")

    source_name_by_file = {
        "review-general.md": "reviewer-general",
        "review-spec.md": "reviewer-spec-audit",
        "review-second.md": "reviewer-second-opinion",
    }

    all_issues: list[Issue] = []
    for path in expected_paths:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        source = source_name_by_file.get(path.name, path.name)
        all_issues.extend(parse_review_issues(content, source=source))

    deduped = deduplicate_issues(all_issues)
    consolidated = build_consolidated_review(args.ticket_id, deduped)

    review_md = artifact_dir / "review.md"
    review_md.write_text(consolidated, encoding="utf-8")

    print(f"  - Written: {review_md}")
    print("\nReview phase complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
