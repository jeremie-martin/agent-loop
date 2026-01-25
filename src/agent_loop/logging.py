"""Logging configuration using loguru."""

import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

# Remove default handler
logger.remove()

# Log directory
LOG_DIR = Path("/tmp/agent-loop")

# Custom formats
LOG_FORMAT_CONSOLE = "<level>{level: <8}</level> | <cyan>{message}</cyan>"
LOG_FORMAT_CONSOLE_VERBOSE = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
LOG_FORMAT_FILE = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}"

# Current log file path (set by configure_logging)
_current_log_file: Path | None = None


def get_log_file() -> Path | None:
    """Return the current log file path, if any."""
    return _current_log_file


def configure_logging(verbosity: int = 0, preset_name: str | None = None) -> Path:
    """Configure loguru based on verbosity level.

    Args:
        verbosity: 0 = INFO, 1 = DEBUG, 2+ = TRACE (includes prompts)
        preset_name: Optional preset name for the log file name

    Returns:
        Path to the log file
    """
    global _current_log_file

    # Remove any existing handlers
    logger.remove()

    # Determine console level and format
    if verbosity == 0:
        console_level = "INFO"
        console_fmt = LOG_FORMAT_CONSOLE
    elif verbosity == 1:
        console_level = "DEBUG"
        console_fmt = LOG_FORMAT_CONSOLE_VERBOSE
    else:
        console_level = "TRACE"
        console_fmt = LOG_FORMAT_CONSOLE_VERBOSE

    # Add console handler
    logger.add(
        sys.stderr,
        format=console_fmt,
        level=console_level,
        colorize=True,
    )

    # Create log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if preset_name:
        log_filename = f"{preset_name}_{timestamp}.log"
    else:
        log_filename = f"agent-loop_{timestamp}.log"

    log_file = LOG_DIR / log_filename
    _current_log_file = log_file

    # Add file handler (always TRACE level for full history)
    logger.add(
        log_file,
        format=LOG_FORMAT_FILE,
        level="TRACE",
        rotation=None,  # No rotation for session logs
        encoding="utf-8",
    )

    logger.debug(f"Log file: {log_file}")

    return log_file


def log_prompt(prompt: str, label: str = "Prompt") -> None:
    """Log a prompt at TRACE level with formatting."""
    logger.trace(f"{label} ({len(prompt)} chars):")
    logger.trace("-" * 60)
    for line in prompt.split("\n"):
        logger.trace(line)
    logger.trace("-" * 60)
