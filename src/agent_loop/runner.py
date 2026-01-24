"""Opencode subprocess wrapper."""

import subprocess
import sys


def run_opencode(prompt: str, model: str | None = None, dry_run: bool = False, verbose: bool = False) -> bool:
    """Run opencode with the given prompt.

    Args:
        prompt: The prompt to send to the agent.
        model: Optional model override.
        dry_run: If True, print the command without executing.
        verbose: If True, print additional information.

    Returns:
        True if the command succeeded, False otherwise.
    """
    cmd = ["opencode", "run", prompt]
    if model:
        cmd.extend(["-m", model])

    if dry_run:
        # Show what would be executed
        print(f"[dry-run] Would execute: opencode run <prompt> -m {model or '(default)'}")
        if verbose:
            print(f"[dry-run] Prompt ({len(prompt)} chars):")
            print("-" * 40)
            print(prompt[:500] + ("..." if len(prompt) > 500 else ""))
            print("-" * 40)
        return True

    if verbose:
        print(f"Running: opencode run <prompt> -m {model or '(default)'}")

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: 'opencode' command not found. Is it installed and in PATH?", file=sys.stderr)
        return False
    except KeyboardInterrupt:
        # Propagate keyboard interrupt
        raise
