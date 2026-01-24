# agent-loop

CLI tool for running LLM agents in iterative refinement loops.

## What it does

agent-loop runs an LLM agent repeatedly through different "modes" (review passes), auto-committing changes after each iteration. When the loop stops (via Ctrl+C or reaching max iterations), it squashes all the iteration commits into one clean commit.

Must be run inside a git repository.

Useful for iterative document review, code refactoring, or any task where you want an agent to make incremental improvements through multiple focused passes.

## Requirements

- `opencode` installed and in your PATH
- The model `zai-coding-plan/glm-4.7` is used (hardcoded; currently not configurable)

## Installation

```bash
# Install as a uv tool (recommended, installs to ~/.local/bin)
uv tool install /path/to/agent-loop

# Or for development (editable)
pip install -e .
```

## Quick Start

```bash
# List available presets
agent-loop list

# Run a preset
agent-loop run docs-review

# Run with verbose output
agent-loop run docs-review -v

# Dry-run (see what would happen)
agent-loop run docs-review --dry-run

# Use a custom preset file
agent-loop run -c ./my-preset.yaml

# Create a new preset template
agent-loop init my-preset
```

## Presets

Presets are YAML files that define modes—review passes that cycle in order. The agent autonomously decides which files to examine and modify.

Simple example:

```yaml
name: my-review
description: Review files for quality

modes:
  - naprompt_suffix: Commit any changes you make. Do not use the "question" tool or any tool requiring user input. Do not use the "question" tool or any tool requiring user input.    prompt: |
      Review the codebase for technical accuracy.
      Fix any errors or outdated information.
      Commit any changes you make.

  - naprompt_suffix: Commit any changes you make. Do not use the "question" tool or any tool requiring user input. Do not use the "question" tool or any tool requiring user input.    prompt: |
      Review for readability. Each sentence should earn its place.
      Tighten prose without losing meaning.
      Commit any changes you make.
```

For a complete example with three well-crafted modes, see the built-in `docs-review` preset: `src/agent_loop/presets/docs-review.yaml`

## Commands

| Command | Description |
|---------|-------------|
| `agent-loop run <preset>` | Run an agent loop with the specified preset |
| `agent-loop run -c, --config <file>` | Run with a custom preset file |
| `agent-loop list` | List available built-in presets |
| `agent-loop init <name>` | Create a new preset template |
| `agent-loop squash --since <hash> [-m <message>]` | Squash commits since a given hash (generates message from commits if `-m` omitted) |
| `agent-loop completion <shell>` | Generate shell completion script (bash/zsh/fish) |

### Run options

- `--dry-run`: Show what would happen without executing
- `-v, --verbose`: Enable verbose output
- `--no-squash`: Don't squash commits when stopping
- `-n, --max-iterations`: Maximum number of iterations to run

## Shell Completion

Enable tab completion for preset names:

```bash
# Bash (~/.bashrc)
eval "$(agent-loop completion bash)"

# Zsh (~/.zshrc)
eval "$(agent-loop completion zsh)"

# Fish
agent-loop completion fish > ~/.config/fish/completions/agent-loop.fish
```

## How it works

1. Load the preset configuration
2. Record the current git commit
3. Loop:
   - Select the next mode (cycles through modes in order)
   - Run `opencode run <prompt>`
   - Commit any changes
 4. When the loop stops (Ctrl+C or max iterations reached): squash all commits since start into one, with the agent generating a meaningful commit message (or falling back to a default if generation fails)

## Prompt Philosophy

Writing effective prompts is key to getting good results from iterative agents:

- **Describe destinations, not steps**: "Concepts appear once" > "remove duplicates"
- **Frame conciseness as quality**: "Every section earns its place" > "keep it short"
- **Use reader-centered language**: "Reads as a coherent whole" puts agents in editor mode
- **One purpose per prompt**: Each mode should have a single, clear focus

See [docs/prompt_philosophy.md](docs/prompt_philosophy.md) for detailed guidance and concrete examples from the built-in presets.

## Contributing

For development guidance, code structure, and contributor notes, see [CLAUDE.md](CLAUDE.md).

## License

MIT
