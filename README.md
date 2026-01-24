# agent-loop

CLI tool for running LLM agents in iterative refinement loops.

## What it does

agent-loop runs an LLM agent repeatedly through different "modes" (review passes), auto-committing changes after each iteration. When you stop the loop (Ctrl+C), it squashes all the iteration commits into one clean commit.

This is useful for iterative document review, code refactoring, or any task where you want an agent to make incremental improvements through multiple focused passes.

## Installation

```bash
pip install -e .
```

Requires `opencode` to be installed and in your PATH.

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
agent-loop run --config ./my-preset.yaml

# Create a new preset template
agent-loop init my-preset
```

## Presets

Presets are YAML files that define:
- **files**: Which files to target (glob patterns)
- **modes**: Review passes that cycle in order
- **settings**: Model, commit message template, etc.

Example preset:

```yaml
name: docs-review
description: Review documentation for quality and accuracy

files:
  pattern: "**/*.md"
  exclude: ["node_modules/**"]

modes:
  - name: alignment
    prompt: |
      Review these files for accuracy against the implementation.
      Files: {files}

  - name: clarity
    prompt: |
      Review for readability. Each sentence should earn its place.
      Files: {files}

settings:
  model: "your-model-here"
  commit_message_template: "[{mode}] iteration {n}"
```

## Commands

| Command | Description |
|---------|-------------|
| `agent-loop run <preset>` | Run an agent loop with the specified preset |
| `agent-loop run --config <file>` | Run with a custom preset file |
| `agent-loop list` | List available built-in presets |
| `agent-loop init <name>` | Create a new preset template |
| `agent-loop squash --since <hash>` | Manually squash commits |

### Run options

- `--dry-run`: Show what would happen without executing
- `-v, --verbose`: Enable verbose output
- `--no-squash`: Don't squash commits when stopping

## How it works

1. Load the preset configuration
2. Record the current git commit
3. Loop:
   - Select the next mode (cycles through modes in order)
   - Resolve the file list from glob patterns
   - Format the prompt with `{files}` placeholder
   - Run `opencode run <prompt>`
   - Commit any changes
4. On Ctrl+C: squash all commits since start into one

## Prompt Philosophy

Writing effective prompts for iterative agents:

- **Describe destinations, not steps**: "Concepts appear once" > "remove duplicates"
- **Frame conciseness as quality**: "Every section earns its place" > "keep it short"
- **Use reader-centered language**: "Reads as a coherent whole" puts agents in editor mode
- **One purpose per prompt**: Each mode should have a single, clear focus

See [docs/prompt_philosophy.md](docs/prompt_philosophy.md) for the full guide.

## License

MIT
