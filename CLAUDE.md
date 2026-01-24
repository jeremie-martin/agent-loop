# CLAUDE.md

Guidance for Claude Code when working with this repository.

## What this project does

agent-loop is a CLI tool that runs LLM agents in iterative refinement loops. It cycles through "modes" (focused review passes), auto-commits changes after each iteration, and squashes all commits into one when you stop.

Key concepts:
- **Presets**: YAML files defining modes and their prompts
- **Modes**: Different focus areas that cycle in order (e.g., accuracy → structure → clarity)
- **Auto-commit**: Each iteration commits changes with `[mode] iteration N`
- **Squash**: On Ctrl+C, all iteration commits are squashed into one

## Quick Commands

```bash
# Install
pip install -e .

# Lint
ruff check .
ruff check . --fix  # auto-fix

# Format
ruff format .

# Tests
pytest -q
```

## Preset Format

Presets are simple YAML files:

```yaml
name: my-preset
description: What this preset does

modes:
  - name: first-pass
    prompt: |
      Instructions for this mode.
      The agent decides what files to work on.
      Commit any changes you make.

  - name: second-pass
    prompt: |
      Instructions for this mode.
      Commit any changes you make.
```

The agent autonomously decides which files to examine and modify. Prompts should describe goals, not list files.

## CLI Commands

| Command | Description |
|---------|-------------|
| `agent-loop run <preset>` | Run a built-in preset |
| `agent-loop run -c <file>` | Run a custom preset file |
| `agent-loop list` | List available presets |
| `agent-loop init <name>` | Create a new preset template |
| `agent-loop squash --since <hash>` | Manually squash commits |

Run options: `--dry-run`, `-v`, `--no-squash`, `-n <max>`

## Code Structure

```
src/agent_loop/
├── cli.py          # Click CLI commands
├── loop.py         # Main loop logic (LoopRunner)
├── preset.py       # Preset loading (Mode, Preset dataclasses)
├── runner.py       # opencode subprocess wrapper
├── git.py          # Git operations (commit, squash)
└── presets/        # Built-in preset YAML files
    └── docs-review.yaml
```

## Writing Prompts

See [docs/prompt_philosophy.md](docs/prompt_philosophy.md) for principles:
- Describe destinations, not steps
- Frame conciseness as quality
- One purpose per mode
