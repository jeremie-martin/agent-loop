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

    def test_loads_prefix_and_suffix(self, tmp_path: Path):
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

    def test_loads_multiline_yaml_strings(self, tmp_path: Path):
        """Multiline YAML strings preserved in prefix/suffix."""
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

        assert preset.prompt_suffix is not None
        assert "First line." in preset.prompt_suffix
        assert "Second line." in preset.prompt_suffix

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

    def test_presets_have_commit_suffix(self):
        """Presets instruct agents to commit at the end."""
        path = find_preset("docs-review")
        preset = load_preset(path)

        assert preset.prompt_suffix is not None
        assert "commit" in preset.prompt_suffix.lower()

    def test_presets_use_self_review_not_external_review(self):
        """Presets embed self-review in prompts instead of external review config."""
        # Presets with 3-step review (includes filter sub-agent)
        three_step_presets = ["security-hardening", "dependency-injection", "interface-segregation"]
        # Presets with 2-step review (no filter, for factual/deterministic tasks)
        two_step_presets = ["docs-review", "dead-code"]

        for preset_name in three_step_presets + two_step_presets:
            path = find_preset(preset_name)
            preset = load_preset(path)

            # No external review config
            assert preset.review is None, f"{preset_name} should not have external review"

            # Self-review pattern in first mode
            first_mode = preset.modes[0]
            assert "sub-agent" in first_mode.prompt.lower(), f"{preset_name} missing sub-agent instruction"

            # Only 3-step presets should have filter
            if preset_name in three_step_presets:
                assert "filter" in first_mode.prompt.lower(), f"{preset_name} should have filter (3-step)"
            else:
                # 2-step presets should NOT have filter
                assert "filter" not in first_mode.prompt.lower(), f"{preset_name} should not have filter (2-step)"

    def test_suffix_applied_to_all_modes(self):
        """Suffix appears in full prompt for every mode."""
        path = find_preset("docs-review")
        assert path is not None
        preset = load_preset(path)

        assert preset.prompt_suffix is not None
        for mode in preset.modes:
            full_prompt = preset.get_full_prompt(mode)
            assert preset.prompt_suffix.strip() in full_prompt
