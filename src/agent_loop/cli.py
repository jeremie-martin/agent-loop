"""Click-based CLI for agent-loop."""

from pathlib import Path

import click

from agent_loop import __version__
from agent_loop.git import generate_squash_message_with_agent, get_commits_since, get_repo, squash_commits
from agent_loop.logging import configure_logging
from agent_loop.loop import run_loop
from agent_loop.preset import find_preset, list_presets, load_preset


def complete_preset_name(ctx, param, incomplete: str) -> list[str]:
    """Shell completion for preset names."""
    presets = list_presets()
    return [name for name, _ in presets if name.startswith(incomplete)]


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Agent Loop - Run LLM agents in iterative refinement loops."""
    pass


@main.command()
@click.argument("preset_name", required=False, shell_complete=complete_preset_name)
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path), help="Path to a custom preset YAML file")
@click.option("--dry-run", is_flag=True, help="Show what would happen without executing")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (-v for debug, -vv for trace with prompts)")
@click.option("--no-squash", is_flag=True, help="Don't squash commits on stop")
@click.option("-n", "--max-iterations", type=int, help="Maximum number of iterations to run")
def run(preset_name: str | None, config: Path | None, dry_run: bool, verbose: int, no_squash: bool, max_iterations: int | None) -> None:
    """Run an agent loop with the specified preset.

    PRESET_NAME is the name of a built-in preset (use 'agent-loop list' to see available presets).
    Alternatively, use --config to specify a custom preset file.

    Press Ctrl+C to stop the loop. By default, all commits made during the loop
    will be squashed into a single commit.
    """
    configure_logging(verbose)

    # Determine which preset to load
    preset_path: Path
    if config:
        preset_path = config
    elif preset_name:
        found = find_preset(preset_name)
        if not found:
            raise click.ClickException(f"Preset '{preset_name}' not found. Use 'agent-loop list' to see available presets.")
        preset_path = found
    else:
        raise click.ClickException("Either PRESET_NAME or --config must be specified")

    try:
        preset = load_preset(preset_path)
    except Exception as e:
        raise click.ClickException(f"Failed to load preset: {e}")

    run_loop(preset, dry_run=dry_run, auto_squash=not no_squash, max_iterations=max_iterations)


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
@click.option("--since", required=True, help="Base commit (exclusive) — commits after this are squashed")
@click.option("--message", "-m", help="Custom commit message (skips agent generation)")
@click.option("--no-agent", is_flag=True, help="Don't use agent to generate commit message")
def squash(since: str, message: str | None, no_agent: bool) -> None:
    """Manually squash commits from a previous run.

    This command squashes all commits from --since up to HEAD into a single commit.
    By default, uses an LLM agent to generate a meaningful commit message.
    """
    try:
        repo = get_repo()
    except RuntimeError as e:
        raise click.ClickException(str(e))

    commits = get_commits_since(repo, since)
    if not commits:
        raise click.ClickException(f"No commits found since {since}")

    click.echo(f"Squashing {len(commits)} commit(s) since {since[:8]}...")

    # Generate message with agent unless --no-agent or --message provided
    if message is None and not no_agent:
        click.echo("Generating commit message with agent...")
        message = generate_squash_message_with_agent(repo, since)
        if message:
            click.echo(f"Generated message: {message.split(chr(10))[0]}")
        else:
            click.echo("Agent failed to generate message, using fallback")

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

prompt_suffix: Commit any changes you make. Do not use the "question" tool or any tool requiring user input.

modes:
  - name: review
    prompt: |
      Review the codebase for quality and accuracy.
      Make improvements where needed.
  - name: refine
    prompt: |
      Refine the codebase based on the previous review.
      Focus on clarity and consistency."""

    path.write_text(template)
    click.echo(f"Created preset: {filename}")
    click.echo(f"Edit the file and run: agent-loop run --config {filename}")


@main.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def completion(shell: str) -> None:
    """Generate shell completion script.

    To enable completions, add to your shell config:

    \b
    # Bash (~/.bashrc)
    eval "$(agent-loop completion bash)"

    \b
    # Zsh (~/.zshrc)
    eval "$(agent-loop completion zsh)"

    \b
    # Fish (~/.config/fish/completions/agent-loop.fish)
    agent-loop completion fish > ~/.config/fish/completions/agent-loop.fish
    """

    from click.shell_completion import get_completion_class

    comp_cls = get_completion_class(shell)
    if comp_cls is None:
        raise click.ClickException(f"Unsupported shell: {shell}")

    comp = comp_cls(main, {}, "agent-loop", "_AGENT_LOOP_COMPLETE")
    click.echo(comp.source())


if __name__ == "__main__":
    main()
