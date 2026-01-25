"""Opencode subprocess wrapper."""

import subprocess

from loguru import logger

from .logging import log_prompt

DEFAULT_MODEL = "zai-coding-plan/glm-4.7"


def run_opencode(prompt: str, dry_run: bool = False) -> bool:
    """Run opencode with the given prompt.

    Args:
        prompt: The prompt to send to the agent.
        dry_run: If True, print the command without executing.

    Returns:
        True if the command succeeded, False otherwise.
    """
    cmd = ["opencode", "run", prompt, "-m", DEFAULT_MODEL]

    if dry_run:
        logger.info(f"[dry-run] Would execute: opencode run <prompt> -m {DEFAULT_MODEL}")
        log_prompt(prompt, "Dry-run prompt")
        return True

    logger.debug(f"Running: opencode run <prompt> -m {DEFAULT_MODEL}")
    log_prompt(prompt, "Agent prompt")

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        logger.error("'opencode' command not found. Is it installed and in PATH?")
        return False
    except KeyboardInterrupt:
        # Propagate keyboard interrupt
        raise
