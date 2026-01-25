"""Tests for preset loading and prompt construction."""

from pathlib import Path
from textwrap import dedent

from agent_loop.preset import Mode, Preset, ReviewConfig, find_preset, list_presets, load_preset


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


class TestReviewConfig:
    """Tests for ReviewConfig parsing."""

    def test_review_config_defaults(self):
        """ReviewConfig has sensible defaults."""
        config = ReviewConfig()

        assert config.enabled is True
        assert config.check_prompt == ""
        assert config.filter_prompt == ""
        assert config.fix_prompt is None

    def test_loads_review_config(self, tmp_path: Path):
        """Review config loaded from YAML."""
        yaml_content = dedent("""
            name: test-preset
            modes:
              - name: review
                prompt: Review.
            review:
              enabled: true
              check_prompt: Check for issues.
              filter_prompt: Filter false positives.
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.review is not None
        assert preset.review.enabled is True
        assert preset.review.check_prompt == "Check for issues."
        assert preset.review.filter_prompt == "Filter false positives."
        assert preset.review.fix_prompt is None

    def test_review_config_disabled(self, tmp_path: Path):
        """Review can be explicitly disabled."""
        yaml_content = dedent("""
            name: test-preset
            modes:
              - name: review
                prompt: Review.
            review:
              enabled: false
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.review is not None
        assert preset.review.enabled is False

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

    def test_review_config_with_fix_prompt(self, tmp_path: Path):
        """Optional fix_prompt is loaded."""
        yaml_content = dedent("""
            name: test-preset
            modes:
              - name: review
                prompt: Review.
            review:
              check_prompt: Check.
              filter_prompt: Filter.
              fix_prompt: Custom fix instructions.
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.review.fix_prompt == "Custom fix instructions."


class TestOptionalFields:
    """Tests for optional fields that default to None and load from YAML."""

    def test_model_defaults_to_none(self):
        """Model defaults to None when not specified."""
        preset = Preset(name="test", description="", modes=[])
        assert preset.model is None

    def test_scope_globs_defaults_to_none(self):
        """scope_globs defaults to None."""
        config = ReviewConfig()
        assert config.scope_globs is None

    def test_model_loaded_from_yaml(self, tmp_path: Path):
        """Model field loaded from YAML."""
        yaml_content = dedent("""
            name: test-preset
            model: custom-model-v1
            modes:
              - name: review
                prompt: Review.
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.model == "custom-model-v1"

    def test_scope_globs_loaded_from_yaml(self, tmp_path: Path):
        """scope_globs loaded from YAML."""
        yaml_content = dedent("""
            name: test-preset
            modes:
              - name: review
                prompt: Review.
            review:
              enabled: true
              check_prompt: Check.
              scope_globs:
                - "*.md"
                - "docs/**"
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.review is not None
        assert preset.review.scope_globs == ["*.md", "docs/**"]

    def test_model_optional_in_yaml(self, tmp_path: Path):
        """Model is None when not specified in YAML."""
        yaml_content = dedent("""
            name: minimal
            modes:
              - name: review
                prompt: Review.
        """)
        preset_file = tmp_path / "minimal.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.model is None

    def test_scope_globs_optional(self, tmp_path: Path):
        """scope_globs is None when not specified."""
        yaml_content = dedent("""
            name: test-preset
            modes:
              - name: review
                prompt: Review.
            review:
              enabled: true
              check_prompt: Check.
        """)
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(yaml_content)

        preset = load_preset(preset_file)

        assert preset.review.scope_globs is None


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
        # Each mode commits at the end after self-review
        assert "commit" in preset.prompt_suffix.lower()

    def test_docs_review_has_self_review(self):
        """docs-review preset has self-orchestrated review in prompts."""
        path = find_preset("docs-review")
        preset = load_preset(path)

        # Self-review is embedded in prompts, not external review config
        assert preset.review is None
        # Verify self-review pattern is in the mode prompts
        quality_mode = next(m for m in preset.modes if m.name == "quality")
        assert "sub-agent" in quality_mode.prompt.lower()
        assert "filter" in quality_mode.prompt.lower()

    def test_frontend_style_has_self_review(self):
        """frontend-style preset has self-orchestrated review in prompts."""
        path = find_preset("frontend-style")
        preset = load_preset(path)

        # Self-review is embedded in prompts, not external review config
        assert preset.review is None
        # Verify self-review pattern is in the mode prompts
        tokens_mode = next(m for m in preset.modes if m.name == "tokens")
        assert "sub-agent" in tokens_mode.prompt.lower()
        assert "filter" in tokens_mode.prompt.lower()

    def test_suffix_applied_to_all_modes(self):
        """Suffix appears in full prompt for every mode."""
        path = find_preset("docs-review")
        preset = load_preset(path)

        for mode in preset.modes:
            full_prompt = preset.get_full_prompt(mode)
            assert preset.prompt_suffix.strip() in full_prompt
