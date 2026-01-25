"""Tests for review cycle logic."""

import pytest
from agent_loop.preset import Mode, Preset, ReviewConfig
from agent_loop.review import build_review_prompt


class TestBuildReviewPrompt:
    """Tests for build_review_prompt()."""

    @pytest.mark.parametrize(
        "preset_desc,config_check,config_filter,expected_content",
        [
            ("Review documentation for accuracy", "Check things.", "Filter things.", "Task: Review documentation for accuracy"),
            ("Test", "Verify all claims.", "Filter out noise.", "**Review scope:**"),
        ],
    )
    def test_includes_task_description_and_prompts(self, preset_desc, config_check, config_filter, expected_content):
        """Prompt includes preset description, check, and filter instructions."""
        preset = Preset(
            name="test",
            description=preset_desc,
            modes=[Mode(name="review", prompt="Review.")],
        )
        config = ReviewConfig(check_prompt=config_check, filter_prompt=config_filter)

        result = build_review_prompt(preset, config)

        assert expected_content in result
        if config_check:
            assert config_check in result
        if config_filter:
            assert config_filter in result

    def test_includes_commit_and_scope_instructions(self):
        """Prompt includes commit instructions and guidance to ignore unrelated files."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig()

        result = build_review_prompt(preset, config)

        assert "**Commit:**" in result
        assert "commit message" in result
        assert "no changes to commit" in result.lower()
        assert "unrelated" in result.lower()
        assert "ignore" in result.lower()

    @pytest.mark.parametrize(
        "fix_prompt,expected_in_result,expected_not_in_result",
        [
            ("Custom fix: do this specific thing.", "Custom fix: do this specific thing.", None),
            (None, "actionable issues", None),
        ],
    )
    def test_fix_prompt_variations(self, fix_prompt, expected_in_result, expected_not_in_result):
        """Custom fix_prompt replaces default fix instructions."""
        preset = Preset(name="test", description="Test", modes=[])

        config = ReviewConfig(
            check_prompt="Check.",
            filter_prompt="Filter.",
            fix_prompt=fix_prompt,
        )
        result = build_review_prompt(preset, config)

        assert expected_in_result.lower() in result.lower()
        if expected_not_in_result:
            assert expected_not_in_result.lower() not in result.lower()

    @pytest.mark.parametrize(
        "check_prompt,filter_prompt,has_check_section,has_filter_section",
        [
            ("", "Filter.", False, True),
            ("Check.", "", True, False),
        ],
    )
    def test_empty_prompt_omits_section(self, check_prompt, filter_prompt, has_check_section, has_filter_section):
        """Empty check_prompt or filter_prompt omits corresponding section."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt=check_prompt, filter_prompt=filter_prompt)
        result = build_review_prompt(preset, config)

        assert ("**Review scope:**" in result) == has_check_section
        assert ("**Before acting, filter your feedback:**" in result) == has_filter_section

    @pytest.mark.parametrize(
        "scope_globs,expected_in_prompt,expected_globs",
        [
            (["*.md", "docs/**"], True, ["`*.md`", "`docs/**`"]),
            (None, False, []),
            ([], False, []),
        ],
    )
    def test_scope_globs_handling(self, scope_globs, expected_in_prompt, expected_globs):
        """scope_globs included in prompt when provided, omitted when empty or None."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(
            check_prompt="Check.",
            filter_prompt="Filter.",
            scope_globs=scope_globs,
        )

        result = build_review_prompt(preset, config)

        assert ("**Files in scope:**" in result) == expected_in_prompt
        for expected_glob in expected_globs:
            assert expected_glob in result


class TestBuildReviewPromptIntegration:
    """Integration tests using realistic config values."""

    def test_docs_review_style_prompt(self):
        """Prompt built with docs-review style config preserves all sections and custom content."""
        preset = Preset(
            name="docs-review",
            description="Review documentation for quality, accuracy, and coherence",
            modes=[
                Mode(name="accuracy", prompt="Check accuracy."),
                Mode(name="structure", prompt="Check structure."),
                Mode(name="clarity", prompt="Check clarity."),
            ],
        )
        config = ReviewConfig(
            check_prompt="""For each modified doc file, verify:
 1. All factual claims are supported by current source code
 2. No content was removed that was actually accurate
 3. Terminology matches what the code uses""",
            filter_prompt="""Filter out:
  - Stylistic preferences that don't affect accuracy
  - Suggestions to add content beyond current scope""",
        )

        result = build_review_prompt(preset, config)

        # Verify task description and all expected sections present
        assert "Task: Review documentation for quality, accuracy, and coherence" in result
        assert "**Review scope:**" in result
        assert "**Before acting, filter your feedback:**" in result
        assert "**Fix:**" in result
        assert "**Commit:**" in result

        # Verify custom check_prompt content preserved
        assert "All factual claims are supported by current source code" in result
        assert "Terminology matches what the code uses" in result

        # Verify custom filter_prompt content preserved
        assert "Stylistic preferences that don't affect accuracy" in result

        # Verify git instructions present
        assert "git status" in result
        assert "git diff" in result
