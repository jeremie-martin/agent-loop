"""Logging configuration using loguru."""

import sys

from loguru import logger

# Remove default handler
logger.remove()

# Custom format for agent-loop
LOG_FORMAT = "<level>{level: <8}</level> | <cyan>{message}</cyan>"
LOG_FORMAT_VERBOSE = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"


def configure_logging(verbosity: int = 0) -> None:
    """Configure loguru based on verbosity level.

    Args:
        verbosity: 0 = INFO, 1 = DEBUG, 2+ = TRACE (includes prompts)
    """
    # Remove any existing handlers
    logger.remove()

    if verbosity == 0:
        level = "INFO"
        fmt = LOG_FORMAT
    elif verbosity == 1:
        level = "DEBUG"
        fmt = LOG_FORMAT_VERBOSE
    else:
        level = "TRACE"
        fmt = LOG_FORMAT_VERBOSE

    logger.add(
        sys.stderr,
        format=fmt,
        level=level,
        colorize=True,
    )


def log_prompt(prompt: str, label: str = "Prompt") -> None:
    """Log a prompt at TRACE level with formatting."""
    logger.trace(f"{label} ({len(prompt)} chars):")
    logger.trace("-" * 60)
    for line in prompt.split("\n"):
        logger.trace(line)
    logger.trace("-" * 60)
