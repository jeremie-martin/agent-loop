# agent-loop

CLI tool for running LLM agents in iterative refinement loops.

## What it does

Runs LLM agents through iterative modes with automatic commit squashing. Useful for iterative document review, code refactoring, or any task requiring incremental improvements through multiple perspectives.

Must be run inside a git repository.

## Requirements

- `opencode` CLI tool installed and in your PATH (the AI agent that executes tasks)
- A configured model for opencode (default: `zai-coding-plan/glm-4.7`, override in preset with `model` field)

## Installation

```bash
# Install as a uv tool (recommended, installs to ~/.local/bin)
uv tool install .

# Reinstall after code changes
uv tool install . --force

# Or for development (editable, changes apply immediately)
pip install -e .
```

## Presets

Presets are YAML files that define modes—focused prompts that cycle in order. The agent autonomously decides which files to examine and modify.

### Using presets

```bash
# List available presets
agent-loop list

# Run a preset
agent-loop run docs-review

# Use a custom preset file
agent-loop run -c ./my-preset.yaml

# Create a new preset file
agent-loop init my-preset
```

For guidance on writing effective prompts, see [PROMPT_PHILOSOPHY.md](PROMPT_PHILOSOPHY.md).

### Preset structure

Simple example:

```yaml
name: my-review
description: Review code for accuracy and clarity

modes:
  - name: accuracy
    prompt: |
      Review the codebase for technical accuracy.
      Fix any errors or outdated information.

  - name: clarity
    prompt: |
      Review for readability. Each sentence should earn its place.
      Tighten prose without losing meaning.

review:
  enabled: true
  check_prompt: Verify accuracy and clarity of all changes.
  filter_prompt: Ignore stylistic suggestions unless they affect meaning.
  fix_prompt: Correct issues flagged in review.
  scope_globs: ["*.md", "*.rst"]
```

Run `agent-loop list` to see available built-in presets.

## Commands

| Command | Description |
|---------|-------------|
| `agent-loop run <preset>` | Run with the specified preset |
| `agent-loop run -c, --config <file>` | Run with a custom preset file |
| `agent-loop list` | List available built-in presets |
| `agent-loop init <name>` | Create a new preset file in current directory |
| `agent-loop squash --since <hash>` | Squash commits into one |
| `agent-loop completion <shell>` | Generate shell completion script |

### Run options

`--dry-run`: Show what would happen without executing

`-v`, `-vv`: Increase verbosity (-v for DEBUG, -vv for TRACE with prompts)

`--no-squash`: Don't squash commits when stopping

`-n`, `--max-iterations`: Maximum number of iterations (unlimited if omitted)

`--max-failures`: Stop after N consecutive agent failures

### Squash options

`--since`: Base commit (exclusive) — all commits after this one are squashed

`-m`, `--message`: Custom commit message (skips LLM generation)

`--no-agent`: Generate bullet-list message from commit subjects instead of using LLM

### Shell completion

```bash
# Bash/Zsh - add to ~/.bashrc or ~/.zshrc
eval "$(agent-loop completion bash)"
eval "$(agent-loop completion zsh)"

# Fish
agent-loop completion fish > ~/.config/fish/completions/agent-loop.fish
```

## Contributing

See [CLAUDE.md](CLAUDE.md) for development setup, code structure overview, and notes on working with the codebase.

## License

MIT
