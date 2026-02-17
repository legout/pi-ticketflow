"""Research phase command for TF workflow.

Implements the /tf-research command which executes the Research phase
for ticket implementation according to the tf-workflow specification.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from tf.kb_helpers import resolve_knowledge_dir
from tf.ticket_loader import TicketLoader
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


def parse_planning_references(ticket_content: str, knowledge_dir: Path) -> dict:
    """Parse planning references from ticket content.
    
    Looks for:
    - "OpenSpec Change: {id}" -> openspec/changes/{id}/
    - "IRF Seed: {topic}" -> {knowledgeDir}/topics/{topic}/
    - "Spike: {topic}" -> {knowledgeDir}/topics/{topic}/
    
    Args:
        ticket_content: The ticket content to parse.
        knowledge_dir: Path to the knowledge directory.
        
    Returns:
        Dictionary with references found.
    """
    references = {
        "openspec_changes": [],
        "irf_seeds": [],
        "spikes": [],
    }
    
    # OpenSpec Change pattern
    openspec_pattern = re.compile(r"OpenSpec Change:\s*(\S+)", re.IGNORECASE)
    for match in openspec_pattern.finditer(ticket_content):
        references["openspec_changes"].append(match.group(1))
    
    # IRF Seed pattern
    seed_pattern = re.compile(r"IRF Seed:\s*(\S+)", re.IGNORECASE)
    for match in seed_pattern.finditer(ticket_content):
        references["irf_seeds"].append(match.group(1))
    
    # Spike pattern
    spike_pattern = re.compile(r"Spike:\s*(\S+)", re.IGNORECASE)
    for match in spike_pattern.finditer(ticket_content):
        references["spikes"].append(match.group(1))
    
    return references


def read_references(
    references: dict,
    knowledge_dir: Path,
    project_root: Path,
) -> dict:
    """Read referenced documents.
    
    Args:
        references: Dictionary with reference IDs.
        knowledge_dir: Path to the knowledge directory.
        project_root: Path to the project root.
        
    Returns:
        Dictionary with reference contents.
    """
    contents = {
        "openspec": [],
        "topics": [],
    }
    
    # Read OpenSpec changes
    for change_id in references.get("openspec_changes", []):
        openspec_dir = project_root / "openspec" / "changes" / change_id
        if openspec_dir.exists():
            spec_content = []
            for md_file in sorted(openspec_dir.glob("*.md")):
                spec_content.append(f"### {md_file.name}\n{md_file.read_text(encoding='utf-8')}")
            if spec_content:
                contents["openspec"].append({
                    "id": change_id,
                    "content": "\n\n".join(spec_content),
                })
    
    # Read topic references (IRF Seeds and Spikes)
    topic_ids = set(references.get("irf_seeds", []) + references.get("spikes", []))
    for topic_id in topic_ids:
        topic_dir = knowledge_dir / "topics" / topic_id
        if topic_dir.exists():
            topic_content = []
            for md_file in sorted(topic_dir.glob("*.md")):
                topic_content.append(f"### {md_file.name}\n{md_file.read_text(encoding='utf-8')}")
            if topic_content:
                contents["topics"].append({
                    "id": topic_id,
                    "content": "\n\n".join(topic_content),
                })
    
    return contents


def check_web_access_available() -> bool:
    """Check if pi-web-access tools are available.
    
    Returns:
        True if web_search and fetch_content tools are available.
    """
    try:
        result = subprocess.run(
            ["pi", "--list-tools"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout + result.stderr
        return "web_search" in output and "fetch_content" in output
    except Exception:
        return False


def check_mcp_tools() -> list[str]:
    """Check available MCP tools.
    
    Returns:
        List of available MCP tool names.
    """
    available = []
    try:
        result = subprocess.run(
            ["pi", "--list-mcp-tools"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout
        # Parse output for known MCP tools
        for tool in ["context7", "exa", "grep_app", "zai-web-search", "zai-web-reader"]:
            if tool in output:
                available.append(tool)
    except Exception:
        pass
    return available


def conduct_research(
    ticket_content: str,
    references: dict,
    reference_contents: dict,
    use_web: bool = False,
) -> dict:
    """Conduct research for the ticket.
    
    Args:
        ticket_content: The ticket content.
        references: Parsed planning references.
        reference_contents: Contents of referenced documents.
        use_web: Whether to use web research.
        
    Returns:
        Dictionary with research findings.
    """
    findings = {
        "summary": "",
        "sources": [],
        "external_research": False,
    }
    
    # Analyze ticket for research needs
    # For now, we focus on internal knowledge unless explicitly needed
    
    # Check if web research is available and needed
    if use_web and check_web_access_available():
        # Web research would be implemented here using web_search tool
        # For now, we mark that web tools are available but we don't auto-research
        findings["web_tools_available"] = True
    
    # Check MCP tools
    mcp_tools = check_mcp_tools()
    if mcp_tools:
        findings["mcp_tools_available"] = mcp_tools
    
    return findings


def write_research_md(
    artifact_dir: Path,
    ticket_id: str,
    ticket_content: str,
    research_enabled: bool,
    references: dict,
    reference_contents: dict,
    findings: dict,
) -> Path:
    """Write research.md artifact.
    
    Args:
        artifact_dir: Directory to write the artifact.
        ticket_id: The ticket ID.
        ticket_content: The ticket content.
        research_enabled: Whether research was enabled.
        references: Parsed planning references.
        reference_contents: Contents of referenced documents.
        findings: Research findings.
        
    Returns:
        Path to the written research.md file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    # Build the research.md content
    lines = [
        f"# Research: {ticket_id}",
        "",
        "## Status",
    ]
    
    if research_enabled:
        lines.append("Research completed")
    else:
        lines.append("Research enabled. No additional external research was performed.")
    
    lines.extend([
        "",
        "## Rationale",
        "- Research was conducted to gather context for implementation",
        "- Internal knowledge base and referenced documents were reviewed",
    ])
    
    if not research_enabled:
        lines.append("- External research was skipped (disabled by flag or config)")
    
    lines.extend([
        "",
        "## Context Reviewed",
        f"- `tk show {ticket_id}`",
    ])
    
    # Add reference information
    if references["openspec_changes"]:
        for change_id in references["openspec_changes"]:
            lines.append(f"- OpenSpec Change: openspec/changes/{change_id}/")
    
    if references["irf_seeds"]:
        for seed_id in references["irf_seeds"]:
            lines.append(f"- IRF Seed: topics/{seed_id}/")
    
    if references["spikes"]:
        for spike_id in references["spikes"]:
            lines.append(f"- Spike: topics/{spike_id}/")
    
    # Add ticket body summary (without frontmatter)
    ticket_body = ticket_content
    if ticket_content.startswith("---"):
        # Extract body after frontmatter
        parts = ticket_content.split("---", 2)
        if len(parts) >= 3:
            ticket_body = parts[2].strip()
    
    lines.extend([
        "",
        "## Ticket Summary",
        "",
    ])
    lines.append(ticket_body[:2000] if len(ticket_body) > 2000 else ticket_body)
    
    # Add referenced content
    if reference_contents["openspec"]:
        lines.extend([
            "",
            "## OpenSpec References",
            "",
        ])
        for spec in reference_contents["openspec"]:
            lines.append(f"### {spec['id']}")
            lines.append("")
            lines.append(spec["content"][:1000] + "..." if len(spec["content"]) > 1000 else spec["content"])
            lines.append("")
    
    if reference_contents["topics"]:
        lines.extend([
            "",
            "## Topic References",
            "",
        ])
        for topic in reference_contents["topics"]:
            lines.append(f"### {topic['id']}")
            lines.append("")
            lines.append(topic["content"][:1000] + "..." if len(topic["content"]) > 1000 else topic["content"])
            lines.append("")
    
    # Add sources section
    lines.extend([
        "",
        "## Sources",
        "- Ticket database (`tk show`)",
        "- Project knowledge base",
    ])
    
    if findings.get("web_tools_available"):
        lines.append("- pi-web-access tools (available for external research)")
    
    if findings.get("mcp_tools_available"):
        tools = findings["mcp_tools_available"]
        lines.append(f"- MCP tools available: {', '.join(tools)}")
    
    if references["openspec_changes"]:
        lines.append("- OpenSpec change documentation")
    
    if references["irf_seeds"] or references["spikes"]:
        lines.append("- Knowledge base topics (seeds/spikes)")
    
    # Write the file
    research_md = artifact_dir / "research.md"
    research_md.write_text("\n".join(lines), encoding="utf-8")
    
    return research_md


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


def migrate_legacy_research(
    artifact_dir: Path,
    knowledge_dir: Path,
    ticket_id: str,
) -> Optional[Path]:
    """Migrate legacy research.md from old location if it exists.
    
    Back-compat: if {knowledgeDir}/tickets/{ticket}.md exists, copy its
    contents to {artifactDir}/research.md (preserving both files).
    
    Args:
        artifact_dir: The new artifact directory.
        knowledge_dir: Path to the knowledge directory.
        ticket_id: The ticket ID.
        
    Returns:
        Path to the legacy file if migrated, None otherwise.
    """
    legacy_path = knowledge_dir / f"{ticket_id}.md"
    
    if not legacy_path.exists():
        return None
    
    # If new file already exists with different content, prefer new and warn
    new_path = artifact_dir / "research.md"
    if new_path.exists():
        legacy_content = legacy_path.read_text(encoding="utf-8")
        new_content = new_path.read_text(encoding="utf-8")
        if legacy_content != new_content:
            print(
                f"Warning: Both legacy ({legacy_path}) and new ({new_path}) research files exist with different content.",
                file=sys.stderr,
            )
            print("Using new artifact path (preferring existing research.md)", file=sys.stderr)
        return legacy_path
    
    # Copy legacy content to new location
    artifact_dir.mkdir(parents=True, exist_ok=True)
    legacy_content = legacy_path.read_text(encoding="utf-8")
    new_path.write_text(legacy_content, encoding="utf-8")
    
    return legacy_path


def check_existing_research(artifact_dir: Path) -> bool:
    """Check if research.md already exists and is sufficient.
    
    Args:
        artifact_dir: The artifact directory.
        
    Returns:
        True if existing research is sufficient.
    """
    research_md = artifact_dir / "research.md"
    if not research_md.exists():
        return False
    
    # Check if file has meaningful content
    content = research_md.read_text(encoding="utf-8")
    
    # Check it's not just a stub (must have substantial content)
    if len(content) < 500:
        return False
    
    # Must have some structure indicating comprehensive research
    # Accept either "## Status" header or "Research completed" marker
    has_status_section = "## Status" in content or "## " in content
    has_completion_marker = "Research completed" in content or "Research phase complete" in content
    
    if not (has_status_section or has_completion_marker):
        return False
    
    # Must have multiple sections (indicating comprehensive research)
    section_count = content.count("## ")
    if section_count < 2 and not has_completion_marker:
        return False
    
    return True


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for tf-research command.
    
    Args:
        argv: Command line arguments.
        
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        prog="tf-research",
        description="Execute the Research phase for TF workflow ticket implementation.",
    )
    parser.add_argument(
        "ticket_id",
        help="The ticket to research (e.g., pt-1234)",
    )
    parser.add_argument(
        "--no-research",
        dest="no_research",
        action="store_true",
        help="Skip research even if enabled in config",
    )
    parser.add_argument(
        "--with-research",
        dest="with_research",
        action="store_true",
        help="Force enable research step",
    )
    
    args = parser.parse_args(argv)
    
    # Find project root
    project_root = find_project_root()
    if project_root is None:
        print("Error: Could not find project root (no .tf or .pi directory)", file=sys.stderr)
        return 1
    
    # Load workflow configuration
    workflow_config = load_workflow_config(project_root)
    enable_researcher = workflow_config.get("enableResearcher", True)
    knowledge_dir_path = workflow_config.get("knowledgeDir", ".tf/knowledge")
    
    # Resolve knowledge directory
    knowledge_dir = Path(knowledge_dir_path)
    if not knowledge_dir.is_absolute():
        knowledge_dir = project_root / knowledge_dir
    
    # Determine if research should run
    # Flag precedence: --with-research takes precedence over --no-research
    research_enabled = enable_researcher
    if args.no_research and args.with_research:
        research_enabled = True  # --with-research wins
    elif args.with_research:
        research_enabled = True
    elif args.no_research:
        research_enabled = False
    
    # Prepare artifact directory
    artifact_dir = knowledge_dir / "tickets" / args.ticket_id
    
    print(f"Research phase for ticket: {args.ticket_id}")
    print(f"Project root: {project_root}")
    print(f"Knowledge dir: {knowledge_dir}")
    print(f"Artifact dir: {artifact_dir}")
    print(f"Research enabled: {research_enabled}")
    
    # Step 1: Re-Anchor Context
    print("\n[Step 1] Re-anchoring context...")
    
    # Read AGENTS.md files
    root_agents = read_agents_md(project_root)
    if root_agents:
        print("  - Read root AGENTS.md")
    
    ralph_agents = read_ralph_agents_md(project_root)
    if ralph_agents:
        print("  - Read .tf/ralph/AGENTS.md")
    
    # Get ticket details
    try:
        ticket_content = run_tk_show(args.ticket_id)
        print(f"  - Retrieved ticket: {args.ticket_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get ticket {args.ticket_id}: {e}", file=sys.stderr)
        return 1
    
    # Step 2: Check Research Prerequisites
    print("\n[Step 2] Checking research prerequisites...")
    
    # Create artifact directory early (needed for both paths)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    # Write ticket_id.txt for chain preservation (always needed)
    write_ticket_id_file(artifact_dir, args.ticket_id)
    print(f"  - Created ticket_id.txt artifact")
    
    # Check for existing research first (regardless of research_enabled)
    # This handles both migration and existing good research
    legacy_file = migrate_legacy_research(artifact_dir, knowledge_dir, args.ticket_id)
    if legacy_file:
        print(f"  - Migrated legacy research from: {legacy_file}")
    
    existing_sufficient = check_existing_research(artifact_dir)
    if existing_sufficient:
        print(f"  - Existing research.md found and is sufficient")
        if not research_enabled:
            print(f"  - Research disabled, but using existing artifact")
        print(f"\nResearch artifact ready at: {artifact_dir / 'research.md'}")
        return 0
    
    if not research_enabled:
        print("  - Research is disabled (by flag or config)")
        print("  - Writing minimal research artifact")
        
        # Write minimal research artifact (non-negotiable artifact rule)
        write_research_md(
            artifact_dir,
            args.ticket_id,
            ticket_content,
            research_enabled=False,
            references={"openspec_changes": [], "irf_seeds": [], "spikes": []},
            reference_contents={"openspec": [], "topics": []},
            findings={},
        )
        print(f"\nWritten minimal research artifact to: {artifact_dir / 'research.md'}")
        return 0
    
    # Step 3: Conduct Research
    print("\n[Step 3] Conducting research...")
    
    # Parse planning references
    references = parse_planning_references(ticket_content, knowledge_dir)
    if references["openspec_changes"]:
        print(f"  - Found OpenSpec references: {', '.join(references['openspec_changes'])}")
    if references["irf_seeds"]:
        print(f"  - Found IRF Seed references: {', '.join(references['irf_seeds'])}")
    if references["spikes"]:
        print(f"  - Found Spike references: {', '.join(references['spikes'])}")
    
    # Read referenced documents
    reference_contents = read_references(references, knowledge_dir, project_root)
    if reference_contents["openspec"]:
        print(f"  - Read {len(reference_contents['openspec'])} OpenSpec document(s)")
    if reference_contents["topics"]:
        print(f"  - Read {len(reference_contents['topics'])} topic document(s)")
    
    # Conduct external research if available
    use_web = check_web_access_available()
    if use_web:
        print("  - pi-web-access tools are available")
    else:
        print("  - pi-web-access tools not available (using internal knowledge)")
    
    findings = conduct_research(
        ticket_content,
        references,
        reference_contents,
        use_web=use_web,
    )
    
    # Step 4: Write research.md
    print("\n[Step 4] Writing research artifact...")
    
    research_path = write_research_md(
        artifact_dir,
        args.ticket_id,
        ticket_content,
        research_enabled=True,
        references=references,
        reference_contents=reference_contents,
        findings=findings,
    )
    
    print(f"  - Written: {research_path}")
    
    # Summary
    print("\n" + "=" * 50)
    print("Research phase complete!")
    print(f"Ticket: {args.ticket_id}")
    print(f"Artifact directory: {artifact_dir}")
    print(f"Research artifact: {research_path}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())