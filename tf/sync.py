from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .frontmatter import sync_models_to_files
from .utils import find_project_root, read_json


def resolve_project_root(args: argparse.Namespace) -> Path:
    if getattr(args, "global_install", False):
        print("tf sync is project-local; do not use --global.", file=sys.stderr)
        raise SystemExit(1)

    if args.project:
        return Path(args.project).expanduser()

    root = find_project_root()
    if root is None:
        return Path.cwd()
    return root


def load_project_config(project_root: Path) -> dict:
    return read_json(project_root / ".tf" / "config" / "settings.json")


def sync_models(project_root: Path, config: dict) -> dict:
    """Sync models from config to all agents and prompts in the project.

    Canonical locations are project-root `agents/` and `prompts/`.
    `.pi/{agents,prompts}` are also synced since that's where Pi loads from.
    """
    results = {"agents": [], "prompts": [], "errors": []}

    # Sync canonical locations
    agents_dir = project_root / "agents"
    prompts_dir = project_root / "prompts"

    if not agents_dir.exists():
        agents_dir = project_root / ".pi" / "agents"

    if not prompts_dir.exists():
        prompts_dir = project_root / ".pi" / "prompts"

    canonical_results = sync_models_to_files(
        config,
        agents_dir if agents_dir.exists() else None,
        prompts_dir if prompts_dir.exists() else None,
    )
    results["agents"].extend(canonical_results["agents"])
    results["prompts"].extend(canonical_results["prompts"])
    results["errors"].extend(canonical_results["errors"])

    # Also sync to .pi/ locations if they exist and are different from canonical
    pi_agents_dir = project_root / ".pi" / "agents"
    pi_prompts_dir = project_root / ".pi" / "prompts"

    if pi_agents_dir.exists() and pi_agents_dir != agents_dir:
        pi_agent_results = sync_models_to_files(
            config,
            pi_agents_dir,
            None,
        )
        # Only add agents that weren't already updated in canonical location
        updated_in_canonical = set(canonical_results["agents"])
        for agent in pi_agent_results["agents"]:
            if agent not in updated_in_canonical:
                results["agents"].append(f"{agent} (in .pi/)")
        results["errors"].extend(pi_agent_results["errors"])

    if pi_prompts_dir.exists() and pi_prompts_dir != prompts_dir:
        pi_prompt_results = sync_models_to_files(
            config,
            None,
            pi_prompts_dir,
        )
        # Only add prompts that weren't already updated in canonical location
        updated_in_canonical = set(canonical_results["prompts"])
        for prompt in pi_prompt_results["prompts"]:
            if prompt not in updated_in_canonical:
                results["prompts"].append(f"{prompt} (in .pi/)")
        results["errors"].extend(pi_prompt_results["errors"])

    return results


def run_sync(args: argparse.Namespace) -> int:
    project_root = resolve_project_root(args)

    # Ensure the workflow bundle exists in the project.
    from . import project_bundle

    project_bundle.install_bundle(project_root)

    config = load_project_config(project_root)
    if not config:
        print(
            f"ERROR: Missing or invalid project config: {project_root / '.tf/config/settings.json'}\n"
            "Run: tf init",
            file=sys.stderr,
        )
        return 1

    print("Syncing models from project meta-model configuration...")
    results = sync_models(project_root, config)

    if results["agents"]:
        print(f"Updated agents: {', '.join(results['agents'])}")
    if results["prompts"]:
        print(f"Updated prompts: {', '.join(results['prompts'])}")

    if results["errors"]:
        print("Errors:", file=sys.stderr)
        for err in results["errors"]:
            print(f"  {err}", file=sys.stderr)
        return 1

    if not results["agents"] and not results["prompts"]:
        print("No changes.")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="tf sync")
    parser.add_argument("--project", help="Operate on project at <path> (default: auto-detect or cwd)")
    parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Not supported (sync is project-local)",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_sync(args)


if __name__ == "__main__":
    raise SystemExit(main())
