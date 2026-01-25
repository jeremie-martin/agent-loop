"""Tests for preset loading and prompt construction."""

from pathlib import Path
from textwrap import dedent
import pytest

from agent_loop.preset import Mode, Preset, ReviewConfig, find_preset, list_presets, load_preset


class TestGetFullPrompt:
    """Tests for Preset.get_full_prompt()."""

    @pytest.mark.parametrize(
        "prefix,suffix,expected",
        [
            (None, None, "Review the code."),
            (None, "Commit changes.", "Review the code.\n\nCommit changes."),
            ("Be thorough.", None, "Be thorough.\n\nReview the code."),
            ("Be thorough.", "Commit changes.", "Be thorough.\n\nReview the code.\n\nCommit changes."),
        ],
    )
    def test_prefix_suffix_combinations(self, prefix, suffix, expected):
        """Prefix and suffix applied in all combinations."""
        preset = Preset(
            name="test",
            description="",
            modes=[],
            prompt_prefix=prefix,
            prompt_suffix=suffix,
        )
        mode = Mode(name="review", prompt="Review the code.")

        result = preset.get_full_prompt(mode)

        assert result == expected

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

        # Trailing/leading whitespace removed from each part
        # No extra blank lines between parts
        assert result == "Prefix with trailing space.\n\nPrompt with whitespace.\n\nSuffix with leading space."
        # Verify no leading/trailing whitespace on the whole result
        assert result == result.strip()


class TestLoadPreset:
    """Tests for load_preset()."""

    @pytest.mark.parametrize(
        "yaml_content,expected_prefix,expected_suffix,check_multiline",
        [
            (
                dedent("""
                    name: test-preset
                    description: A test preset
                    prompt_prefix: Always be kind.
                    prompt_suffix: Commit your work.
                    modes:
                      - name: review
                        prompt: Review the code.
                """),
                "Always be kind.",
                "Commit your work.",
                False,
            ),
            (
                dedent("""
                    name: test
                    prompt_suffix: |
                      First line.
                      Second line.
                    modes:
                      - name: review
                        prompt: Review.
                """),
                None,
                None,
                True,
            ),
        ],
    )
    def test_loads_prefix_suffix(self, tmp_path: Path, yaml_content, expected_prefix, expected_suffix, check_multiline):
        """Prefix and suffix loaded from YAML, including multiline."""
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        if check_multiline:
            assert preset.prompt_suffix is not None
            assert "First line." in preset.prompt_suffix
            assert "Second line." in preset.prompt_suffix
        else:
            if expected_prefix is not None:
                assert preset.prompt_prefix == expected_prefix
            if expected_suffix is not None:
                assert preset.prompt_suffix == expected_suffix

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


class TestReviewConfig:
    """Tests for ReviewConfig parsing."""

    def test_review_config_defaults(self):
        """ReviewConfig has sensible defaults."""
        config = ReviewConfig()

        assert config.enabled is True
        assert config.check_prompt == ""
        assert config.filter_prompt == ""
        assert config.fix_prompt is None

    @pytest.mark.parametrize(
        "yaml_content,expected_enabled,expected_check,expected_filter,expected_fix",
        [
            (
                dedent("""
                    name: test-preset
                    modes:
                      - name: review
                        prompt: Review.
                    review:
                      enabled: true
                      check_prompt: Check for issues.
                      filter_prompt: Filter false positives.
                      fix_prompt: Custom fix instructions.
                """),
                True,
                "Check for issues.",
                "Filter false positives.",
                "Custom fix instructions.",
            ),
            (
                dedent("""
                    name: test-preset
                    modes:
                      - name: review
                        prompt: Review.
                    review:
                      enabled: false
                """),
                False,
                "",
                "",
                None,
            ),
        ],
    )
    def test_review_config_variations(self, tmp_path: Path, yaml_content, expected_enabled, expected_check, expected_filter, expected_fix):
        """Review config supports enabled/disabled, optional fields, and fix_prompt."""
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.review is not None
        assert preset.review.enabled is expected_enabled
        assert preset.review.check_prompt == expected_check
        assert preset.review.filter_prompt == expected_filter
        assert preset.review.fix_prompt == expected_fix

    def test_review_config_optional(self, tmp_path: Path):
        """Review config is None when not specified."""
        yaml_content = dedent("""
            name: minimal
            modes:
              - name: review
                prompt: Review.
        """)
        preset_file = tmp_path / "minimal.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.review is None


class TestBuiltinPresets:
    """Tests for built-in presets."""

    def test_all_presets_load(self):
        """All built-in presets load successfully with required fields."""
        presets = list_presets()
        assert len(presets) > 0

        for name, description in presets:
            preset_path = find_preset(name)
            assert preset_path is not None, f"Preset {name} not found"
            preset = load_preset(preset_path)
            assert preset.name == name, f"Preset name mismatch for {name}"
            assert len(preset.modes) > 0, f"Preset {name} has no modes"
            assert all(m.name and m.prompt for m in preset.modes), f"Preset {name} has invalid modes"

    @pytest.mark.parametrize(
        "preset_name,mode_name",
        [
            ("docs-review", "quality"),
            ("frontend-style", "tokens"),
        ],
    )
    def test_self_review_presets_have_embedded_review(self, preset_name, mode_name):
        """Self-review presets have commit suffix and embedded review patterns."""
        path = find_preset(preset_name)
        assert path is not None

        preset = load_preset(path)

        # Has prompt_suffix with commit instruction (docs-review)
        if preset_name == "docs-review":
            assert preset.prompt_suffix is not None
            assert "commit" in preset.prompt_suffix.lower()

        # Self-review is embedded in prompts, not external review config
        assert preset.review is None

        # Verify self-review pattern is in the mode prompts
        mode = next(m for m in preset.modes if m.name == mode_name)
        assert "sub-agent" in mode.prompt.lower()
        assert "filter" in mode.prompt.lower()

    def test_suffix_applied_to_all_modes(self):
        """Suffix appears in full prompt for every mode."""
        path = find_preset("docs-review")
        assert path is not None
        preset = load_preset(path)

        assert preset.prompt_suffix is not None
        for mode in preset.modes:
            full_prompt = preset.get_full_prompt(mode)
            assert preset.prompt_suffix.strip() in full_prompt
