"""Click-based CLI for agent-loop."""

from pathlib import Path

import click

from . import __version__
from .git import get_commits_since, get_repo, squash_commits
from .loop import run_loop
from .preset import find_preset, list_presets, load_preset


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Agent Loop - Run LLM agents in iterative refinement loops."""
    pass


@main.command()
@click.argument("preset_name", required=False)
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path), help="Path to a custom preset YAML file")
@click.option("--dry-run", is_flag=True, help="Show what would happen without executing")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--no-squash", is_flag=True, help="Don't squash commits on stop")
def run(preset_name: str | None, config: Path | None, dry_run: bool, verbose: bool, no_squash: bool) -> None:
    """Run an agent loop with the specified preset.

    PRESET_NAME is the name of a built-in preset (use 'agent-loop list' to see available presets).
    Alternatively, use --config to specify a custom preset file.

    Press Ctrl+C to stop the loop. By default, all commits made during the loop
    will be squashed into a single commit.
    """
    # Determine which preset to load
    if config:
        preset_path = config
    elif preset_name:
        preset_path = find_preset(preset_name)
        if not preset_path:
            raise click.ClickException(f"Preset '{preset_name}' not found. Use 'agent-loop list' to see available presets.")
    else:
        raise click.ClickException("Either PRESET_NAME or --config must be specified")

    try:
        preset = load_preset(preset_path)
    except Exception as e:
        raise click.ClickException(f"Failed to load preset: {e}")

    run_loop(preset, dry_run=dry_run, verbose=verbose, auto_squash=not no_squash)


@main.command("list")
def list_cmd() -> None:
    """List available built-in presets."""
    presets = list_presets()

    if not presets:
        click.echo("No built-in presets found.")
        click.echo("Create a preset file and use: agent-loop run --config <path>")
        return

    click.echo("Available presets:\n")
    for name, description in presets:
        click.echo(f"  {name}")
        if description:
            click.echo(f"    {description}")
        click.echo()


@main.command()
@click.option("--since", required=True, help="Commit hash to squash from (exclusive)")
@click.option("--message", "-m", help="Custom commit message (auto-generated if not specified)")
def squash(since: str, message: str | None) -> None:
    """Manually squash commits from a previous run.

    This command squashes all commits from --since up to HEAD into a single commit.
    """
    try:
        repo = get_repo()
    except RuntimeError as e:
        raise click.ClickException(str(e))

    commits = get_commits_since(repo, since)
    if not commits:
        raise click.ClickException(f"No commits found since {since}")

    click.echo(f"Squashing {len(commits)} commit(s) since {since[:8]}...")

    if squash_commits(repo, since, message):
        click.echo("Squash complete.")
    else:
        raise click.ClickException("Squash failed")


@main.command()
@click.argument("name")
def init(name: str) -> None:
    """Initialize a new preset file.

    Creates a new preset YAML file with the given NAME in the current directory.
    """
    filename = f"{name}.yaml"
    path = Path.cwd() / filename

    if path.exists():
        raise click.ClickException(f"File already exists: {filename}")

    template = f"""name: {name}
description: Add your description here

# File targeting (optional)
files:
  pattern: "**/*.md"
  exclude:
    - "node_modules/**"
    - ".git/**"

# Modes cycle through in order
modes:
  - name: review
    prompt: |
      Review these files for quality and accuracy.

      Files:
      {{files}}

  - name: refine
    prompt: |
      Refine these files based on the previous review.

      Files:
      {{files}}

# Optional settings
settings:
  # model: "your-model-here"
  commit_message_template: "[{{mode}}] iteration {{n}}"
"""

    path.write_text(template)
    click.echo(f"Created preset: {filename}")
    click.echo(f"Edit the file and run: agent-loop run --config {filename}")


if __name__ == "__main__":
    main()
