"""Preset loading and validation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

BUILTIN_PRESETS_DIR = Path(__file__).parent.parent.parent / "presets"


@dataclass
class Mode:
    """A single mode in a preset's review cycle."""

    name: str
    prompt: str


@dataclass
class FileConfig:
    """File targeting configuration."""

    pattern: str = "**/*"
    exclude: list[str] = field(default_factory=list)


@dataclass
class Settings:
    """Optional preset settings."""

    model: str | None = None
    commit_message_template: str = "[{mode}] iteration {n}"


@dataclass
class Preset:
    """A loaded preset configuration."""

    name: str
    description: str
    modes: list[Mode]
    files: FileConfig = field(default_factory=FileConfig)
    settings: Settings = field(default_factory=Settings)
    path: Path | None = None


def _parse_modes(data: list[dict[str, Any]]) -> list[Mode]:
    """Parse mode definitions from YAML data."""
    modes = []
    for m in data:
        if "name" not in m or "prompt" not in m:
            raise ValueError("Each mode must have 'name' and 'prompt' fields")
        modes.append(Mode(name=m["name"], prompt=m["prompt"]))
    return modes


def _parse_file_config(data: dict[str, Any] | None) -> FileConfig:
    """Parse file configuration from YAML data."""
    if data is None:
        return FileConfig()
    return FileConfig(
        pattern=data.get("pattern", "**/*"),
        exclude=data.get("exclude", []),
    )


def _parse_settings(data: dict[str, Any] | None) -> Settings:
    """Parse settings from YAML data."""
    if data is None:
        return Settings()
    return Settings(
        model=data.get("model"),
        commit_message_template=data.get("commit_message_template", "[{mode}] iteration {n}"),
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
        files=_parse_file_config(data.get("files")),
        settings=_parse_settings(data.get("settings")),
        path=path,
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


def resolve_files(file_config: FileConfig, base_dir: Path | None = None) -> list[Path]:
    """Resolve file patterns to actual file paths."""
    base = base_dir or Path.cwd()
    files = list(base.glob(file_config.pattern))

    # Apply exclusions
    excluded = set()
    for exclude_pattern in file_config.exclude:
        excluded.update(base.glob(exclude_pattern))

    return sorted(f for f in files if f not in excluded and f.is_file())
