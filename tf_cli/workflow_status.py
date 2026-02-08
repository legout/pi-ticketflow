"""Workflow status utility - quick overview of IRF workflow state."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple


class WorkflowStats(NamedTuple):
    """Statistics about the current workflow state."""
    open_tickets: int
    ready_tickets: int
    in_progress: int
    recent_closed: int
    has_ralph: bool
    knowledge_entries: int


@dataclass
class WorkflowStatus:
    """Complete workflow status report."""
    stats: WorkflowStats
    project_root: Path
    config_exists: bool


def count_tickets_by_status(tickets_dir: Path) -> dict[str, int]:
    """Count tickets by their status from frontmatter."""
    counts = {"open": 0, "ready": 0, "in_progress": 0, "closed": 0}
    
    if not tickets_dir.exists():
        return counts
    
    for ticket_file in tickets_dir.glob("*.md"):
        try:
            content = ticket_file.read_text()
            # Simple frontmatter parsing
            if "status: open" in content:
                if "deps: []" in content or "deps:" not in content:
                    counts["ready"] += 1
                counts["open"] += 1
            elif "status: closed" in content:
                counts["closed"] += 1
            elif "status: in_progress" in content:
                counts["in_progress"] += 1
        except Exception:
            continue
    
    return counts


def get_knowledge_entries(knowledge_dir: Path) -> int:
    """Count knowledge base entries."""
    if not knowledge_dir.exists():
        return 0
    
    entries = 0
    for subdir in ["topics", "spikes", "tickets"]:
        subpath = knowledge_dir / subdir
        if subpath.exists():
            entries += len([x for x in subpath.iterdir() if x.is_dir()])
    
    return entries


def get_workflow_status(project_root: Path | str | None = None) -> WorkflowStatus:
    """Get complete workflow status for the project."""
    if project_root is None:
        # Try to find project root by looking for .tf directory
        cwd = Path.cwd()
        project_root = cwd
        while project_root != project_root.parent:
            if (project_root / ".tf").exists():
                break
            project_root = project_root.parent
    
    project_root = Path(project_root)
    tf_dir = project_root / ".tf"
    tickets_dir = tf_dir / "tickets"
    knowledge_dir = tf_dir / "knowledge"
    ralph_dir = tf_dir / "ralph"
    
    ticket_counts = count_tickets_by_status(tickets_dir)
    
    stats = WorkflowStats(
        open_tickets=ticket_counts["open"],
        ready_tickets=ticket_counts["ready"],
        in_progress=ticket_counts["in_progress"],
        recent_closed=ticket_counts["closed"],
        has_ralph=ralph_dir.exists(),
        knowledge_entries=get_knowledge_entries(knowledge_dir),
    )
    
    return WorkflowStatus(
        stats=stats,
        project_root=project_root,
        config_exists=(tf_dir / "config" / "settings.json").exists(),
    )


def print_status(status: WorkflowStatus | None = None) -> None:
    """Print formatted workflow status to stdout."""
    if status is None:
        status = get_workflow_status()
    
    print("\n🔧 TF Workflow Status")
    print("=" * 40)
    print(f"📁 Project: {status.project_root}")
    print(f"⚙️  Config: {'✅' if status.config_exists else '❌'}")
    print()
    print("📊 Tickets")
    print(f"   Open:       {status.stats.open_tickets}")
    print(f"   Ready:      {status.stats.ready_tickets}")
    print(f"   In Progress:{status.stats.in_progress}")
    print(f"   Closed:     {status.stats.recent_closed}")
    print()
    print("📚 Knowledge Base")
    print(f"   Entries:    {status.stats.knowledge_entries}")
    print()
    print("🤖 Ralph Loop")
    print(f"   Status:     {'✅ Active' if status.stats.has_ralph else '❌ Not configured'}")
    print("=" * 40)


if __name__ == "__main__":
    print_status()
