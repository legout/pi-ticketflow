from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

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


def resolve_meta_model(config: dict, name: str) -> dict:
    meta_models = config.get("metaModels", {}) or {}
    if name in meta_models:
        return meta_models[name]

    agents = config.get("agents", {}) or {}
    if name in agents:
        meta_key = agents[name]
        return meta_models.get(meta_key, {"model": name, "thinking": "medium"})

    prompts = config.get("prompts", {}) or {}
    if name in prompts:
        meta_key = prompts[name]
        return meta_models.get(meta_key, {"model": name, "thinking": "medium"})

    return {"model": name, "thinking": "medium"}


def _update_frontmatter(content: str, model: str, thinking: str) -> str:
    frontmatter_pattern = r"^(---\s*\n)(.*?)(\n---\s*\n)"

    def replace(match):
        prefix, fm, suffix = match.group(1), match.group(2), match.group(3)

        if re.search(r"^model:\s*", fm, re.MULTILINE):
            fm = re.sub(r"^model:\s*.*$", f"model: {model}", fm, flags=re.MULTILINE)
        else:
            fm += f"\nmodel: {model}"

        if re.search(r"^thinking:\s*", fm, re.MULTILINE):
            fm = re.sub(r"^thinking:\s*.*$", f"thinking: {thinking}", fm, flags=re.MULTILINE)
        else:
            fm += f"\nthinking: {thinking}"

        return prefix + fm + suffix

    return re.sub(frontmatter_pattern, replace, content, flags=re.DOTALL)


def update_agent_frontmatter(agent_path: Path, config: dict, agent_name: str) -> bool:
    content = agent_path.read_text(encoding="utf-8")
    resolved = resolve_meta_model(config, agent_name)
    model = resolved.get("model", "openai-codex/gpt-5.1-codex-mini")
    thinking = resolved.get("thinking", "medium")

    new_content = _update_frontmatter(content, model, thinking)
    if new_content != content:
        agent_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def update_prompt_frontmatter(prompt_path: Path, config: dict, prompt_name: str) -> bool:
    content = prompt_path.read_text(encoding="utf-8")
    resolved = resolve_meta_model(config, prompt_name)
    model = resolved.get("model", "openai-codex/gpt-5.1-codex-mini")
    thinking = resolved.get("thinking", "medium")

    new_content = _update_frontmatter(content, model, thinking)
    if new_content != content:
        prompt_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def sync_models(project_root: Path, config: dict) -> dict:
    results = {"agents": [], "prompts": [], "errors": []}

    agents_dir = project_root / ".pi" / "agents"
    if agents_dir.exists():
        for agent_file in agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            try:
                if update_agent_frontmatter(agent_file, config, agent_name):
                    results["agents"].append(agent_name)
            except Exception as e:
                results["errors"].append(f"agents/{agent_file.name}: {e}")

    prompts_dir = project_root / ".pi" / "prompts"
    if prompts_dir.exists():
        for prompt_file in prompts_dir.glob("*.md"):
            prompt_name = prompt_file.stem
            try:
                if update_prompt_frontmatter(prompt_file, config, prompt_name):
                    results["prompts"].append(prompt_name)
            except Exception as e:
                results["errors"].append(f"prompts/{prompt_file.name}: {e}")

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
