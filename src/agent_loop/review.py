"""Review cycle logic for validating changes after mode cycles."""

from loguru import logger

from .preset import Preset, ReviewConfig
from .runner import run_opencode


def build_review_prompt(preset: Preset, config: ReviewConfig) -> str:
    """Build a self-contained review prompt from preset and config.

    The prompt includes all context needed for the agent to:
    1. Understand the task scope
    2. Review only relevant changes
    3. Filter feedback to avoid false positives
    4. Fix genuine issues
    5. Commit with a meaningful message
    """
    parts = []

    # Task context and scope
    parts.append(f"Task: {preset.description}")
    parts.append("")
    parts.append("A cycle of work has been completed. Review and finalize the changes.")
    parts.append("")
    parts.append("Use `git diff` to see what was changed. Focus only on changes related to the task above.")
    parts.append("If there are unrelated modified files, ignore them—do not include them in your review or commit.")
    parts.append("")

    # Review instructions
    if config.check_prompt:
        parts.append("**Review scope:**")
        parts.append(config.check_prompt.strip())
        parts.append("")

    # Filter instructions
    if config.filter_prompt:
        parts.append("**Before acting, filter your feedback:**")
        parts.append(config.filter_prompt.strip())
        parts.append("")

    # Fix instructions
    parts.append("**Fix:**")
    if config.fix_prompt:
        parts.append(config.fix_prompt.strip())
    else:
        parts.append("If actionable issues remain after filtering, fix them.")
    parts.append("")

    # Commit instructions
    parts.append("**Commit:**")
    parts.append("Stage and commit only the files related to the task.")
    parts.append("Use a clear commit message summarizing what was accomplished.")
    parts.append("If there are no changes to commit (nothing relevant was modified), do nothing.")

    return "\n".join(parts)


def run_review_cycle(preset: Preset, config: ReviewConfig, dry_run: bool = False) -> bool:
    """Run a review cycle using a self-contained review agent.

    Args:
        preset: The preset being used (for context).
        config: The review configuration.
        dry_run: If True, print the command without executing.

    Returns:
        True if the review completed successfully, False otherwise.
    """
    if not config.enabled:
        logger.debug("Review cycle disabled, skipping")
        return True

    prompt = build_review_prompt(preset, config)
    logger.debug(f"Built review prompt ({len(prompt)} chars)")

    return run_opencode(prompt=prompt, dry_run=dry_run)
