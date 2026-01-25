# agent-loop

CLI tool for running LLM agents in iterative refinement loops.

## What it does

Runs LLM agents through iterative review passes, auto-committing changes after each iteration. When the loop stops (via Ctrl+C or reaching max iterations), it squashes all the iteration commits into one clean commit.

Must be run inside a git repository.

Useful for iterative document review, code refactoring, or any task where you want an agent to make incremental improvements through multiple focused passes.

## Requirements

- `opencode` installed and in your PATH
- Uses model `zai-coding-plan/glm-4.7` (currently not configurable)

## Installation

```bash
# Install as a uv tool (recommended, installs to ~/.local/bin)
uv tool install /path/to/agent-loop

# Update after code changes (must use --force to rebuild)
uv tool install . --force

# Or for development (editable, changes apply immediately)
pip install -e .
```

### Versioning

Versions are automatically derived from git tags using `hatch-vcs`:
- Tag `v0.1.0` → version `0.1.0`
- New commits on tagged version → `0.1.1.dev1+HASH`
- Create a new release: `git tag v0.2.0` then reinstall

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

prompt_suffix: |
  Commit any changes you make.
  Do not use the "question" tool or any tool requiring user input.

modes:
  - name: accuracy
    prompt: |
      Review the codebase for technical accuracy.
      Fix any errors or outdated information.

  - name: clarity
    prompt: |
      Review for readability. Each sentence should earn its place.
      Tighten prose without losing meaning.

# Optional: run a review agent after each complete cycle
review:
  enabled: true
  check_prompt: |
    Verify that changes are correct and consistent.
  filter_prompt: |
    Filter out stylistic opinions. Only act on real issues.
```

Built-in presets include accessibility, api-docs, code-refactor, dead-code, dependency-audit, docs-review, error-handling, frontend-style, migration, prose-tightening, security-review, test-strengthening, and type-tightening. Use `agent-loop list` to see them all.

## Commands

| Command | Description |
|---------|-------------|
| `agent-loop run <preset>` | Run an agent loop with the specified preset |
| `agent-loop run -c, --config <file>` | Run with a custom preset file |
| `agent-loop list` | List available built-in presets |
| `agent-loop init <name>` | Create a new preset template |
| `agent-loop squash --since <hash>` | Squash commits after the given hash into one (uses LLM to generate message) |
| `agent-loop completion <shell>` | Generate shell completion script (bash/zsh/fish) |

### Run options

- `--dry-run`: Show what would happen without executing
- `-v, --verbose`: Enable verbose output
- `--no-squash`: Don't squash commits when stopping
- `-n, --max-iterations`: Maximum number of iterations to run

### Squash options

- `--since`: Base commit (exclusive) — all commits after this one are squashed
- `-m, --message`: Custom commit message (skips LLM generation)
- `--no-agent`: Use simple bullet-list fallback instead of LLM

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
3. Loop through modes:
   - Select the next mode (cycles through modes in order)
   - Run `opencode run <prompt>` (agent commits its own changes)
   - After completing all modes in a cycle: run optional review agent
4. When the loop stops (Ctrl+C or max iterations reached): squash all commits into one clean commit with an LLM-generated message

### Review cycles

Presets can include a `review` block that runs a validation agent after each complete cycle of modes. This catches issues like:
- Factual drift in documentation
- Broken CSS token references
- Inconsistent replacements

The review agent receives a composed prompt with check instructions, filter instructions (to avoid false positives), and commit instructions. See [docs/prompt_philosophy.md](docs/prompt_philosophy.md) for design principles.

## Prompt Philosophy

Writing effective prompts is key to getting good results from iterative agents. See [docs/prompt_philosophy.md](docs/prompt_philosophy.md) for detailed guidance and concrete examples from the built-in presets.

## Contributing

For development guidance, code structure, and contributor notes, see [CLAUDE.md](CLAUDE.md).

## License

MIT
