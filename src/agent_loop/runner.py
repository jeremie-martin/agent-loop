"""Opencode subprocess wrapper."""

import subprocess

from loguru import logger

from .logging import log_prompt

DEFAULT_MODEL = "zai-coding-plan/glm-4.7"


def run_opencode(prompt: str, dry_run: bool = False, model: str | None = None) -> bool:
    """Run opencode with the given prompt.

    Args:
        prompt: The prompt to send to the agent.
        dry_run: If True, print the command without executing.
        model: Model to use. Defaults to DEFAULT_MODEL.

    Returns:
        True if the command succeeded, False otherwise.
    """
    model = model or DEFAULT_MODEL
    cmd = ["opencode", "run", prompt, "-m", model]

    if dry_run:
        logger.info(f"[dry-run] Would execute: opencode run <prompt> -m {model}")
        log_prompt(prompt, "Dry-run prompt")
        return True

    logger.debug(f"Running: opencode run <prompt> -m {model}")
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
