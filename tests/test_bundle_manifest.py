"""Regression tests for bundled workflow assets."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_install_manifest_includes_ralph_loop_prompt() -> None:
    """`tf init` should install /ralph-loop prompt."""
    manifest_path = Path("config/install-manifest.txt")
    lines = [
        line.strip()
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    assert "prompts/ralph-loop.md" in lines


def test_settings_maps_ralph_loop_prompt_to_meta_model() -> None:
    """Prompt model sync config should include /ralph-loop mapping."""
    settings_path = Path("config/settings.json")
    settings = json.loads(settings_path.read_text(encoding="utf-8"))

    assert settings.get("prompts", {}).get("ralph-loop") == "general"
