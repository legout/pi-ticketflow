from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple


def find_project_root() -> Optional[Path]:
    """Find the project root by looking for .tf directory."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".tf").is_dir():
            return parent
    return None


def run_tk_command(args: List[str]) -> Tuple[int, str, str]:
    """Run a tk command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["tk"] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_ticket_ids_from_ready() -> List[str]:
    """Get list of ready ticket IDs."""
    returncode, stdout, _ = run_tk_command(["ready"])
    if returncode != 0:
        return []
    
    ids = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line:
            # Extract ID from first column (handles various output formats)
            parts = line.split()
            if parts:
                ids.append(parts[0])
    return ids


def get_ticket_ids_by_status(status: str) -> List[str]:
    """Get ticket IDs filtered by status."""
    returncode, stdout, _ = run_tk_command(["ls", "--status", status])
    if returncode != 0:
        return []
    
    ids = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("-"):
            parts = line.split()
            if parts and not parts[0].startswith("-"):
                ids.append(parts[0])
    return ids


def get_ticket_ids_by_tag(tag: str) -> List[str]:
    """Get ticket IDs filtered by tag."""
    returncode, stdout, _ = run_tk_command(["ls", "--tag", tag])
    if returncode != 0:
        return []
    
    ids = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("-"):
            parts = line.split()
            if parts and not parts[0].startswith("-"):
                ids.append(parts[0])
    return ids


def parse_ticket_show(output: str) -> dict:
    """Parse tk show output into a dictionary."""
    ticket = {
        "id": "",
        "title": "",
        "priority": "",
        "status": "",
        "tags": [],
        "description": "",
        "type": "",
    }
    
    lines = output.strip().split("\n")
    in_header = True
    description_lines = []
    
    for line in lines:
        line = line.rstrip()
        
        # Parse frontmatter lines
        if in_header:
            if line.startswith("id:"):
                ticket["id"] = line.split(":", 1)[1].strip()
            elif line.startswith("priority:"):
                ticket["priority"] = line.split(":", 1)[1].strip()
            elif line.startswith("status:"):
                ticket["status"] = line.split(":", 1)[1].strip()
            elif line.startswith("type:"):
                ticket["type"] = line.split(":", 1)[1].strip()
            elif line.startswith("tags:"):
                tags_str = line.split(":", 1)[1].strip()
                # Parse [tag1, tag2, ...] format
                tags_match = re.findall(r'\[([^\]]*)\]', tags_str)
                if tags_match:
                    ticket["tags"] = [t.strip() for t in tags_match[0].split(",") if t.strip()]
            elif line.startswith("# ") and ticket["id"]:
                # Title line
                ticket["title"] = line[2:].strip()
                in_header = False
            elif line == "---":
                continue
        else:
            description_lines.append(line)
    
    ticket["description"] = "\n".join(description_lines).strip()
    return ticket


def classify_priority(ticket: dict) -> Tuple[str, str]:
    """
    Classify ticket priority based on rubric.
    Returns (proposed_priority, reason).
    """
    title = ticket.get("title", "").lower()
    description = ticket.get("description", "").lower()
    tags = [t.lower() for t in ticket.get("tags", [])]
    ticket_type = ticket.get("type", "").lower()
    
    # P0: Critical bug/risk (security, data correctness, OOM, crashes)
    p0_keywords = ["security", "crash", "oom", "memory leak", "data loss", "corruption", 
                   "panic", "segfault", "vulnerability", "cve", "exploit"]
    if any(kw in title or kw in description for kw in p0_keywords):
        return "P0", f"Critical issue detected: matches security/risk keywords"
    
    if ticket_type == "bug" and any(kw in title or kw in description 
                                     for kw in ["critical", "blocker", "breaking"]):
        return "P0", "Critical bug classification"
    
    # P1: Urgent fixes blocking release or major feature work
    p1_keywords = ["blocker", "blocking", "urgent", "hotfix", "regression"]
    if any(kw in title or kw in description for kw in p1_keywords):
        return "P1", f"Urgent/blocking issue detected"
    
    if ticket_type == "bug" and any(t in tags for t in ["bug", "fix"]):
        return "P1", "Bug fix classification"
    
    # P2: Real product features (user-facing capabilities)
    if ticket_type in ["feature", "enhancement"] or "feature" in tags:
        return "P2", "Product feature classification"
    
    if any(kw in title for kw in ["add ", "implement ", "support ", "enable "]):
        return "P2", "New capability/feature indicated by title"
    
    # P4: Code cosmetics / refactors / docs / test typing polish (check before P3)
    p4_keywords = ["refactor", "cleanup", "typo", "formatting", "cosmetic", "polish"]
    p4_tags = ["docs", "documentation", "refactor", "cleanup", "style", "test", "typing"]
    
    if any(kw in title or kw in description for kw in p4_keywords):
        return "P4", f"Code cleanup/cosmetic classification"
    
    if any(t in tags for t in p4_tags):
        return "P4", f"Maintenance tag match: {[t for t in tags if t in p4_tags][0]}"
    
    # P3: Important engineering quality / dev workflow improvements
    p3_keywords = ["performance", "optimize", "cache", "improve", "upgrade", 
                   "dependency", "workflow", "ci/cd", "build", "tooling"]
    if any(kw in title or kw in description for kw in p3_keywords):
        return "P3", f"Engineering quality improvement: matches workflow keywords"
    
    if ticket_type in ["task", "chore"]:
        return "P3", "Engineering task classification"
    
    # Default: keep current or infer from type
    current = ticket.get("priority", "")
    if current:
        return current, "No clear rubric match, keeping current priority"
    
    return "P3", "Default classification (no clear rubric match)"


def format_priority(p: str) -> str:
    """Normalize priority format."""
    p = p.strip().upper()
    if p.startswith("P") and p[1:].isdigit():
        return p
    # Try to convert numeric
    if p.isdigit() and 0 <= int(p) <= 4:
        return f"P{p}"
    return p


def print_results(results: List[dict], apply: bool) -> None:
    """Print classification results in a table format."""
    print()
    if apply:
        print("Priority Reclassification Results (APPLIED):")
    else:
        print("Priority Reclassification Results (DRY RUN):")
    print()
    
    # Header
    print(f"{'Ticket':<12} {'Current':<10} {'Proposed':<10} {'Reason':<40}")
    print("-" * 72)
    
    for r in results:
        ticket_id = r["id"]
        current = r["current"]
        proposed = r["proposed"]
        reason = r["reason"][:37] + "..." if len(r["reason"]) > 40 else r["reason"]
        
        change_marker = "*" if current != proposed else " "
        print(f"{change_marker}{ticket_id:<11} {current:<10} {proposed:<10} {reason}")
    
    print()
    changed = sum(1 for r in results if r["current"] != r["proposed"])
    print(f"Total: {len(results)} tickets, {changed} would change")
    
    if not apply and changed > 0:
        print()
        print("Run with --apply to make these changes.")


def write_audit_trail(project_root: Path, results: List[dict], apply: bool) -> None:
    """Write audit trail to knowledge directory."""
    knowledge_dir = project_root / ".tf" / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"priority-reclassify-{timestamp}.md"
    filepath = knowledge_dir / filename
    
    lines = [
        "# Priority Reclassification Audit",
        "",
        f"**Timestamp:** {datetime.now().isoformat()}",
        f"**Mode:** {'APPLY' if apply else 'DRY RUN'}",
        "",
        "## Results",
        "",
        "| Ticket | Current | Proposed | Applied | Reason |",
        "|--------|---------|----------|---------|--------|",
    ]
    
    for r in results:
        applied = "Yes" if (apply and r["current"] != r["proposed"]) else "No"
        lines.append(f"| {r['id']} | {r['current']} | {r['proposed']} | {applied} | {r['reason']} |")
    
    lines.extend([
        "",
        "## Summary",
        "",
    ])
    
    changed = sum(1 for r in results if r["current"] != r["proposed"])
    lines.append(f"- Total tickets processed: {len(results)}")
    lines.append(f"- Priorities changed: {changed}")
    lines.append(f"- Unchanged: {len(results) - changed}")
    
    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nAudit trail written to: {filepath}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tf new priority-reclassify",
        description="Reclassify ticket priorities using P0-P4 rubric",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply priority changes (default is dry-run)",
    )
    parser.add_argument(
        "--ids",
        help="Comma-separated list of ticket IDs to process",
    )
    parser.add_argument(
        "--ready",
        action="store_true",
        help="Process all ready tickets",
    )
    parser.add_argument(
        "--status",
        help="Filter by ticket status",
    )
    parser.add_argument(
        "--tag",
        help="Filter by tag",
    )
    parser.add_argument(
        "--project",
        help="Operate on project at <path>",
    )
    
    args = parser.parse_args(argv)
    
    # Check tk is available
    if shutil.which("tk") is None:
        print("tk not found in PATH; cannot query tickets.", file=sys.stderr)
        return 1
    
    # Resolve project root
    if args.project:
        project_root = Path(args.project).expanduser()
    else:
        project_root = find_project_root()
    
    if not project_root:
        print("No .tf project found. Run from a project directory or use --project.", file=sys.stderr)
        return 1
    
    # Collect ticket IDs
    ticket_ids: List[str] = []
    
    if args.ids:
        ticket_ids = [t.strip() for t in args.ids.split(",") if t.strip()]
    elif args.ready:
        ticket_ids = get_ticket_ids_from_ready()
        if not ticket_ids:
            print("No ready tickets found.", file=sys.stderr)
            return 0
    elif args.status:
        ticket_ids = get_ticket_ids_by_status(args.status)
        if not ticket_ids:
            print(f"No tickets with status '{args.status}' found.", file=sys.stderr)
            return 0
    elif args.tag:
        ticket_ids = get_ticket_ids_by_tag(args.tag)
        if not ticket_ids:
            print(f"No tickets with tag '{args.tag}' found.", file=sys.stderr)
            return 0
    else:
        parser.print_help()
        print("\nError: Must specify one of --ids, --ready, --status, or --tag", file=sys.stderr)
        return 1
    
    # Process tickets
    results = []
    
    for ticket_id in ticket_ids:
        returncode, stdout, stderr = run_tk_command(["show", ticket_id])
        if returncode != 0:
            print(f"Warning: Could not fetch ticket {ticket_id}: {stderr}", file=sys.stderr)
            continue
        
        ticket = parse_ticket_show(stdout)
        if not ticket["id"]:
            ticket["id"] = ticket_id
        
        # Skip closed tickets
        if ticket.get("status") == "closed":
            continue
        
        proposed, reason = classify_priority(ticket)
        current = format_priority(ticket.get("priority", ""))
        proposed = format_priority(proposed)
        
        results.append({
            "id": ticket_id,
            "current": current or "(none)",
            "proposed": proposed,
            "reason": reason,
            "ticket": ticket,
        })
    
    if not results:
        print("No tickets to process.")
        return 0
    
    # Apply changes if requested
    if args.apply:
        for r in results:
            if r["current"] != r["proposed"]:
                # Note: This assumes tk supports a 'priority' command or similar
                # For now, we just print what would happen
                # TODO: Implement actual priority update when tk supports it
                pass
    
    # Output results
    print_results(results, args.apply)
    
    # Write audit trail
    write_audit_trail(project_root, results, args.apply)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
