"""Preset loading and validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

BUILTIN_PRESETS_DIR = Path(__file__).parent / "presets"


@dataclass
class Mode:
    """A single mode in a preset's review cycle."""

    name: str
    prompt: str


@dataclass
class ReviewConfig:
    """Configuration for the review phase after each cycle."""

    enabled: bool = True
    check_prompt: str = ""
    filter_prompt: str = ""
    fix_prompt: str | None = None
    scope_globs: list[str] | None = None


@dataclass
class Preset:
    """A loaded preset configuration."""

    name: str
    description: str
    modes: list[Mode]
    path: Path | None = None
    prompt_prefix: str | None = None
    prompt_suffix: str | None = None
    review: ReviewConfig | None = None
    model: str | None = None

    def get_full_prompt(self, mode: Mode) -> str:
        """Return mode prompt with prefix/suffix applied."""
        parts = []
        if self.prompt_prefix:
            parts.append(self.prompt_prefix.rstrip())
        parts.append(mode.prompt.strip())
        if self.prompt_suffix:
            parts.append(self.prompt_suffix.strip())
        return "\n\n".join(parts)


def _parse_modes(data: list[dict[str, Any]]) -> list[Mode]:
    """Parse mode definitions from YAML data."""
    modes = []
    for m in data:
        if "name" not in m or "prompt" not in m:
            raise ValueError("Each mode must have 'name' and 'prompt' fields")
        modes.append(Mode(name=m["name"], prompt=m["prompt"]))
    return modes


def _parse_review_config(data: dict[str, Any] | None) -> ReviewConfig | None:
    """Parse review configuration from YAML data."""
    if data is None:
        return None
    return ReviewConfig(
        enabled=data.get("enabled", True),
        check_prompt=data.get("check_prompt", ""),
        filter_prompt=data.get("filter_prompt", ""),
        fix_prompt=data.get("fix_prompt"),
        scope_globs=data.get("scope_globs"),
    )


def load_preset(path: Path) -> Preset:
    """Load a preset from a YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Preset file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid preset format in {path}")

    if "name" not in data:
        raise ValueError(f"Preset must have 'name' field: {path}")
    if "modes" not in data or not data["modes"]:
        raise ValueError(f"Preset must have at least one mode: {path}")

    return Preset(
        name=data["name"],
        description=data.get("description", ""),
        modes=_parse_modes(data["modes"]),
        path=path,
        prompt_prefix=data.get("prompt_prefix"),
        prompt_suffix=data.get("prompt_suffix"),
        review=_parse_review_config(data.get("review")),
        model=data.get("model"),
    )


def find_preset(name: str) -> Path | None:
    """Find a preset by name in the built-in presets directory."""
    preset_path = BUILTIN_PRESETS_DIR / f"{name}.yaml"
    if preset_path.exists():
        return preset_path
    return None


def list_presets() -> list[tuple[str, str]]:
    """List all available built-in presets.

    Returns a list of (name, description) tuples.
    """
    presets = []
    if BUILTIN_PRESETS_DIR.exists():
        for path in sorted(BUILTIN_PRESETS_DIR.glob("*.yaml")):
            try:
                preset = load_preset(path)
                presets.append((preset.name, preset.description))
            except Exception:
                presets.append((path.stem, "(invalid preset)"))
    return presets
