"""Config command for interactive tf settings management.

Provides a user-friendly way to configure tf settings without editing JSON manually.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_settings_path(project_root: Optional[Path] = None) -> Path:
    """Get the path to settings.json."""
    if project_root is None:
        project_root = Path.cwd()
    return project_root / ".tf" / "config" / "settings.json"


def load_settings(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Load settings from file."""
    settings_path = get_settings_path(project_root)
    if settings_path.exists():
        try:
            with open(settings_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"ERROR: Could not load settings: {e}", file=sys.stderr)
            return {}
    return {}


def save_settings(settings: Dict[str, Any], project_root: Optional[Path] = None) -> bool:
    """Save settings to file."""
    settings_path = get_settings_path(project_root)
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except IOError as e:
        print(f"ERROR: Could not save settings: {e}", file=sys.stderr)
        return False


def prompt_input(message: str, default: Optional[str] = None) -> str:
    """Prompt for input with optional default."""
    if default:
        reply = input(f"{message} [{default}]: ").strip()
        return reply if reply else default
    return input(f"{message}: ").strip()


def prompt_choice(message: str, choices: List[str], default: Optional[str] = None) -> str:
    """Prompt for a choice from a list."""
    print(f"\n{message}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")

    while True:
        reply = input("Select (number or name): ").strip()
        if not reply and default:
            return default
        if reply.isdigit() and 1 <= int(reply) <= len(choices):
            return choices[int(reply) - 1]
        if reply in choices:
            return reply
        print("Invalid choice. Please try again.")


def prompt_yes_no(message: str, default_yes: bool) -> bool:
    """Prompt for yes/no input."""
    suffix = "(Y/n)" if default_yes else "(y/N)"
    reply = input(f"{message} {suffix} ").strip().lower()
    if not reply:
        return default_yes
    return reply.startswith("y")


# Predefined model options with descriptions
MODEL_PRESETS = {
    "openai-codex/gpt-5.3-codex": "Best for complex tasks, high quality",
    "openai-codex/gpt-5.2-codex": "Good balance of quality and speed",
    "openai-codex/gpt-5.1-codex-mini": "Faster, cheaper, good for reviews",
    "minimax/MiniMax-M2.5": "Strong reasoning, good for implementation",
    "kimi-coding/k2p5": "Fast and capable general-purpose model",
    "zai/glm-5": "Good for fix iterations",
    "chutes/zai-org/GLM-4.7-Flash": "Very fast and cheap for simple tasks",
}

META_MODEL_ROLES = {
    "worker": "Implementation (writes code)",
    "research": "Research and information gathering",
    "fast": "Fast/cheap tasks (close, summaries)",
    "general": "General-purpose orchestration",
    "review-general": "General code review",
    "review-spec": "Specification compliance audit",
    "review-secop": "Second-opinion review",
    "fixer": "Fix iterations after review",
    "planning": "Planning and specification",
}

REVIEWER_OPTIONS = {
    "reviewer-general": "General code quality review",
    "reviewer-spec-audit": "Specification compliance check",
    "reviewer-second-opinion": "Alternative perspective review",
}


def show_current_config(settings: Dict[str, Any]) -> None:
    """Display current configuration."""
    print("\n" + "=" * 50)
    print("Current Configuration")
    print("=" * 50)

    meta_models = settings.get("metaModels", {})
    print("\nMeta-Models (by role):")
    for role, desc in META_MODEL_ROLES.items():
        config = meta_models.get(role, {})
        model = config.get("model", "not set")
        thinking = config.get("thinking", "medium")
        print(f"  {role:20} -> {model}")
        print(f"                       thinking: {thinking}")

    workflow = settings.get("workflow", {})
    print("\nWorkflow Settings:")
    print(f"  enableResearcher:     {workflow.get('enableResearcher', True)}")
    print(f"  researchParallelAgents: {workflow.get('researchParallelAgents', 3)}")
    print(f"  enableFixer:          {workflow.get('enableFixer', True)}")
    print(f"  enableCloser:         {workflow.get('enableCloser', True)}")
    print(f"  enableQualityGate:    {workflow.get('enableQualityGate', False)}")

    reviewers = workflow.get("enableReviewers", [])
    print(f"  enableReviewers:      {', '.join(reviewers) if reviewers else 'none'}")

    print("\n" + "=" * 50)


def configure_meta_model(settings: Dict[str, Any], role: str) -> bool:
    """Configure a meta-model for a specific role."""
    print(f"\nConfiguring: {role}")
    print(f"Purpose: {META_MODEL_ROLES.get(role, 'Unknown')}")

    if "metaModels" not in settings:
        settings["metaModels"] = {}

    current = settings["metaModels"].get(role, {})
    current_model = current.get("model", "")

    # Show preset options
    print("\nAvailable models:")
    model_ids = list(MODEL_PRESETS.keys())
    for i, model_id in enumerate(model_ids, 1):
        desc = MODEL_PRESETS[model_id]
        marker = " [current]" if model_id == current_model else ""
        print(f"  {i}. {model_id}")
        print(f"     {desc}{marker}")
    print("  c. Custom model ID")
    print("  s. Skip (keep current)")

    reply = input("Select: ").strip().lower()
    if reply == "s":
        return False

    if reply == "c":
        new_model = input("Enter model ID: ").strip()
    elif reply.isdigit() and 1 <= int(reply) <= len(model_ids):
        new_model = model_ids[int(reply) - 1]
    else:
        print("Invalid selection.")
        return False

    if not new_model:
        return False

    # Configure thinking level
    current_thinking = current.get("thinking", "medium")
    thinking = prompt_choice(
        "Thinking level:",
        ["low", "medium", "high"],
        default=current_thinking,
    )

    settings["metaModels"][role] = {
        "model": new_model,
        "thinking": thinking,
    }
    print(f"✓ Set {role} -> {new_model} (thinking: {thinking})")
    return True


def configure_reviewers(settings: Dict[str, Any]) -> bool:
    """Configure which reviewers to enable."""
    print("\nConfiguring Reviewers")
    print("=" * 40)

    if "workflow" not in settings:
        settings["workflow"] = {}

    current = settings["workflow"].get("enableReviewers", [
        "reviewer-general",
        "reviewer-spec-audit",
        "reviewer-second-opinion",
    ])

    enabled = []
    for reviewer_id, description in REVIEWER_OPTIONS.items():
        is_enabled = reviewer_id in current
        if prompt_yes_no(f"Enable {reviewer_id}?\n  ({description})", is_enabled):
            enabled.append(reviewer_id)

    settings["workflow"]["enableReviewers"] = enabled
    print(f"✓ Enabled reviewers: {', '.join(enabled) if enabled else 'none'}")
    return True


def configure_workflow(settings: Dict[str, Any]) -> bool:
    """Configure workflow settings."""
    print("\nConfiguring Workflow Settings")
    print("=" * 40)

    if "workflow" not in settings:
        settings["workflow"] = {}

    workflow = settings["workflow"]

    # Researcher
    workflow["enableResearcher"] = prompt_yes_no(
        "Enable research step before implementation?",
        workflow.get("enableResearcher", True),
    )

    if workflow["enableResearcher"]:
        current = workflow.get("researchParallelAgents", 3)
        reply = input(f"Number of parallel research agents [{current}]: ").strip()
        workflow["researchParallelAgents"] = int(reply) if reply.isdigit() else current

    # Fixer
    workflow["enableFixer"] = prompt_yes_no(
        "Enable fix step after review?",
        workflow.get("enableFixer", True),
    )

    # Closer
    workflow["enableCloser"] = prompt_yes_no(
        "Enable close step after fixes?",
        workflow.get("enableCloser", True),
    )

    # Quality gate
    workflow["enableQualityGate"] = prompt_yes_no(
        "Enable quality gate (blocks closing if issues found)?",
        workflow.get("enableQualityGate", False),
    )

    print("✓ Workflow settings updated")
    return True


def run_interactive_config(settings: Dict[str, Any]) -> bool:
    """Run interactive configuration wizard."""
    print("\n" + "=" * 50)
    print("TF Configuration Wizard")
    print("=" * 50)
    print("\nThis wizard helps you configure tf settings.")
    print("Press Ctrl+C at any time to cancel without saving.")

    try:
        while True:
            print("\nOptions:")
            print("  1. Configure all meta-models (recommended)")
            print("  2. Configure specific meta-model")
            print("  3. Configure reviewers")
            print("  4. Configure workflow settings")
            print("  5. Show current config")
            print("  6. Save and exit")
            print("  7. Exit without saving")

            reply = input("\nSelect: ").strip()

            if reply == "1":
                for role in META_MODEL_ROLES:
                    if configure_meta_model(settings, role):
                        pass
            elif reply == "2":
                role = prompt_choice(
                    "Select role:",
                    list(META_MODEL_ROLES.keys()),
                )
                configure_meta_model(settings, role)
            elif reply == "3":
                configure_reviewers(settings)
            elif reply == "4":
                configure_workflow(settings)
            elif reply == "5":
                show_current_config(settings)
            elif reply == "6":
                return True
            elif reply == "7":
                return False
            else:
                print("Invalid choice.")

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return False


def set_value(settings: Dict[str, Any], key: str, value: str) -> bool:
    """Set a specific config value by key path."""
    # Parse key path like "metaModels.worker.model"
    parts = key.split(".")
    current = settings

    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    # Try to parse value as JSON (for numbers, booleans, lists)
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value

    current[parts[-1]] = parsed
    return True


def get_value(settings: Dict[str, Any], key: str) -> Optional[Any]:
    """Get a specific config value by key path."""
    parts = key.split(".")
    current = settings

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def run_config(args: argparse.Namespace) -> int:
    """Run the config command."""
    project_root = Path(args.project).expanduser() if args.project else Path.cwd()

    # Ensure we're in a tf project
    settings_path = get_settings_path(project_root)
    if not settings_path.exists() and not args.project:
        print("ERROR: No tf project found. Run 'tf init' first or specify --project.", file=sys.stderr)
        return 1

    settings = load_settings(project_root)

    # Handle direct get/set operations
    if args.get:
        value = get_value(settings, args.get)
        if value is not None:
            print(json.dumps(value, indent=2) if isinstance(value, (dict, list)) else value)
            return 0
        else:
            print(f"Key not found: {args.get}", file=sys.stderr)
            return 1

    if args.set:
        if "=" not in args.set:
            print("ERROR: --set requires KEY=VALUE format", file=sys.stderr)
            return 1
        key, value = args.set.split("=", 1)
        if set_value(settings, key, value):
            if save_settings(settings, project_root):
                print(f"✓ Set {key} = {value}")
                # Auto-sync after setting
                print("Run 'tf sync' to apply changes to prompts/agents.")
                return 0
        return 1

    if args.list:
        show_current_config(settings)
        return 0

    # Interactive mode
    if run_interactive_config(settings):
        if save_settings(settings, project_root):
            print("\n✓ Configuration saved.")
            if prompt_yes_no("Run 'tf sync' now to apply changes?", default_yes=True):
                from tf import sync
                return sync.main([f"--project={project_root}"] if args.project else [])
        return 0
    else:
        print("\nNo changes saved.")
        return 0


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for config command."""
    parser = argparse.ArgumentParser(
        description="Configure tf settings interactively or directly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tf config                          # Interactive wizard
  tf config --list                   # Show current config
  tf config --get metaModels.worker.model
  tf config --set metaModels.worker.model=kimi-coding/k2p5
  tf config --set workflow.enableResearcher=false
        """,
    )
    parser.add_argument(
        "--project",
        help="Project path (default: current directory)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List current configuration",
    )
    parser.add_argument(
        "--get",
        metavar="KEY",
        help="Get a specific config value (dot notation: metaModels.worker.model)",
    )
    parser.add_argument(
        "--set",
        metavar="KEY=VALUE",
        help="Set a specific config value (dot notation: metaModels.worker.model=value)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for config command."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_config(args)


if __name__ == "__main__":
    raise SystemExit(main())
