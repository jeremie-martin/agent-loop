"""Tests for review cycle logic."""

from agent_loop.preset import Mode, Preset, ReviewConfig
from agent_loop.review import build_review_prompt


class TestBuildReviewPrompt:
    """Tests for build_review_prompt()."""

    def test_includes_task_description(self):
        """Prompt includes preset description as task context."""
        preset = Preset(
            name="test",
            description="Review documentation for accuracy",
            modes=[Mode(name="review", prompt="Review.")],
        )
        config = ReviewConfig(check_prompt="Check things.", filter_prompt="Filter things.")

        result = build_review_prompt(preset, config)

        assert "Task: Review documentation for accuracy" in result

    def test_includes_check_prompt(self):
        """Prompt includes the check instructions."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt="Verify all claims.", filter_prompt="Filter out noise.")

        result = build_review_prompt(preset, config)

        assert "**Review scope:**" in result
        assert "Verify all claims." in result

    def test_includes_filter_prompt(self):
        """Prompt includes the filter instructions."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt="Check.", filter_prompt="Filter false positives.")

        result = build_review_prompt(preset, config)

        assert "**Before acting, filter your feedback:**" in result
        assert "Filter false positives." in result

    def test_includes_commit_instructions(self):
        """Prompt includes commit instructions."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig()

        result = build_review_prompt(preset, config)

        assert "**Commit:**" in result
        assert "commit message" in result

    def test_handles_no_changes(self):
        """Prompt handles case where there are no changes."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig()

        result = build_review_prompt(preset, config)

        assert "no changes to commit" in result.lower()

    def test_scopes_to_relevant_files(self):
        """Prompt tells agent to ignore unrelated files."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig()

        result = build_review_prompt(preset, config)

        assert "unrelated" in result.lower()
        assert "ignore" in result.lower()

    def test_uses_custom_fix_prompt(self):
        """Custom fix_prompt replaces default fix instructions."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(
            check_prompt="Check.",
            filter_prompt="Filter.",
            fix_prompt="Custom fix: do this specific thing.",
        )

        result = build_review_prompt(preset, config)

        assert "Custom fix: do this specific thing." in result

    def test_default_fix_prompt(self):
        """Default fix instructions used when fix_prompt not specified."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt="Check.", filter_prompt="Filter.")

        result = build_review_prompt(preset, config)

        assert "actionable issues" in result.lower()

    def test_empty_check_prompt_omits_section(self):
        """Empty check_prompt omits the Review scope section."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt="", filter_prompt="Filter.")

        result = build_review_prompt(preset, config)

        assert "**Review scope:**" not in result
        assert "**Before acting, filter your feedback:**" in result

    def test_empty_filter_prompt_omits_section(self):
        """Empty filter_prompt omits the filter section."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt="Check.", filter_prompt="")

        result = build_review_prompt(preset, config)

        assert "**Review scope:**" in result
        assert "**Before acting, filter your feedback:**" not in result

    def test_scope_globs_included_in_prompt(self):
        """scope_globs interpolated into prompt."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(
            check_prompt="Check.",
            filter_prompt="Filter.",
            scope_globs=["*.md", "docs/**"],
        )

        result = build_review_prompt(preset, config)

        assert "**Files in scope:**" in result
        assert "`*.md`" in result
        assert "`docs/**`" in result

    def test_scope_globs_omitted_when_none(self):
        """No scope section when scope_globs is None."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt="Check.", filter_prompt="Filter.")

        result = build_review_prompt(preset, config)

        assert "**Files in scope:**" not in result

    def test_scope_globs_omitted_when_empty(self):
        """No scope section when scope_globs is empty list."""
        preset = Preset(name="test", description="Test", modes=[])
        config = ReviewConfig(check_prompt="Check.", filter_prompt="Filter.", scope_globs=[])

        result = build_review_prompt(preset, config)

        assert "**Files in scope:**" not in result


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

        # Verify task description included
        assert "Task: Review documentation for quality, accuracy, and coherence" in result

        # Verify all expected sections present
        assert "**Review scope:**" in result
        assert "**Before acting, filter your feedback:**" in result
        assert "**Fix:**" in result
        assert "**Commit:**" in result

        # Verify custom check_prompt content preserved
        assert "All factual claims are supported by current source code" in result
        assert "Terminology matches what the code uses" in result

        # Verify custom filter_prompt content preserved
        assert "Stylistic preferences that don't affect accuracy" in result
        assert "Suggestions to add content beyond current scope" in result

        # Verify git instructions present
        assert "git status" in result
        assert "git diff" in result
