# CLAUDE.md

Guidance for Claude Code when working with this repository.

*For project overview and usage, see the [README](README.md).*

## Quick Commands

```bash
# Lint
ruff check .
ruff check . --fix  # auto-fix

# Format
ruff format .
```

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

## Key Files

- `cli.py` - Entry point, command definitions
- `loop.py` - Main iteration loop, mode cycling, squash logic
- `preset.py` - YAML parsing, Mode/Preset dataclasses
- `runner.py` - Subprocess wrapper for opencode CLI
- `git.py` - Commit and squash operations
- `presets/*.yaml` - Built-in presets (docs-review)

## Development Notes

When making changes:
- Test the full loop flow: preset loading → iteration → commit → squash
- Verify mode cycling wraps correctly (last mode → first mode)
- Check that commit messages follow the format `[mode] iteration N`
- Ensure squash only squashes iteration commits, not unrelated changes

## Writing Prompts

For work on prompt-related tasks, see [docs/prompt_philosophy.md](docs/prompt_philosophy.md).
