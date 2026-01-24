"""Tests for preset loading and prompt construction."""

from pathlib import Path
from textwrap import dedent

from agent_loop.preset import Mode, Preset, find_preset, list_presets, load_preset


class TestGetFullPrompt:
    """Tests for Preset.get_full_prompt()."""

    def test_prompt_only(self):
        """Mode prompt returned as-is when no prefix/suffix."""
        preset = Preset(name="test", description="", modes=[])
        mode = Mode(name="review", prompt="Review the code.")

        result = preset.get_full_prompt(mode)

        assert result == "Review the code."

    def test_with_suffix(self):
        """Suffix appended with blank line separator."""
        preset = Preset(name="test", description="", modes=[], prompt_suffix="Commit changes.")
        mode = Mode(name="review", prompt="Review the code.")

        result = preset.get_full_prompt(mode)

        assert result == "Review the code.\n\nCommit changes."

    def test_with_prefix(self):
        """Prefix prepended with blank line separator."""
        preset = Preset(name="test", description="", modes=[], prompt_prefix="Be thorough.")
        mode = Mode(name="review", prompt="Review the code.")

        result = preset.get_full_prompt(mode)

        assert result == "Be thorough.\n\nReview the code."

    def test_with_both(self):
        """Both prefix and suffix applied correctly."""
        preset = Preset(
            name="test",
            description="",
            modes=[],
            prompt_prefix="Be thorough.",
            prompt_suffix="Commit changes.",
        )
        mode = Mode(name="review", prompt="Review the code.")

        result = preset.get_full_prompt(mode)

        assert result == "Be thorough.\n\nReview the code.\n\nCommit changes."

    def test_strips_whitespace(self):
        """Whitespace stripped from all parts before joining."""
        preset = Preset(
            name="test",
            description="",
            modes=[],
            prompt_prefix="Prefix with trailing space.  \n",
            prompt_suffix="\n  Suffix with leading space.",
        )
        mode = Mode(name="review", prompt="\n  Prompt with whitespace.  \n")

        result = preset.get_full_prompt(mode)

        assert result == "Prefix with trailing space.\n\nPrompt with whitespace.\n\nSuffix with leading space."


class TestLoadPreset:
    """Tests for load_preset()."""

    def test_loads_prefix_suffix(self, tmp_path: Path):
        """Prefix and suffix loaded from YAML."""
        yaml_content = dedent("""
            name: test-preset
            description: A test preset
            prompt_prefix: Always be kind.
            prompt_suffix: Commit your work.
            modes:
              - name: review
                prompt: Review the code.
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.prompt_prefix == "Always be kind."
        assert preset.prompt_suffix == "Commit your work."

    def test_prefix_suffix_optional(self, tmp_path: Path):
        """Prefix and suffix default to None when not specified."""
        yaml_content = dedent("""
            name: minimal
            modes:
              - name: review
                prompt: Review.
        """)
        preset_file = tmp_path / "minimal.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.prompt_prefix is None
        assert preset.prompt_suffix is None

    def test_multiline_suffix(self, tmp_path: Path):
        """Multiline prefix/suffix preserved."""
        yaml_content = dedent("""
            name: test
            prompt_suffix: |
              First line.
              Second line.
            modes:
              - name: review
                prompt: Review.
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert "First line." in preset.prompt_suffix
        assert "Second line." in preset.prompt_suffix


class TestBuiltinPresets:
    """Tests for built-in presets."""

    def test_all_presets_load(self):
        """All built-in presets load without error."""
        presets = list_presets()
        assert len(presets) > 0

        for name, description in presets:
            assert "(invalid preset)" not in description, f"Preset {name} failed to load"

    def test_docs_review_has_suffix(self):
        """docs-review preset uses prompt_suffix."""
        path = find_preset("docs-review")
        assert path is not None

        preset = load_preset(path)

        assert preset.prompt_suffix is not None
        assert "Commit" in preset.prompt_suffix

    def test_suffix_applied_to_all_modes(self):
        """Suffix appears in full prompt for every mode."""
        path = find_preset("docs-review")
        preset = load_preset(path)

        for mode in preset.modes:
            full_prompt = preset.get_full_prompt(mode)
            assert preset.prompt_suffix.strip() in full_prompt
