# CLAUDE.md

Guidance for Claude Code when working with this repository.

*For project overview and usage, see the [README](README.md).*

## Development Commands

```bash
# Lint
ruff check .
ruff check . --fix  # auto-fix

# Format
ruff format .

# Type check
mypy src/

# Test
pytest
```

## Code Structure

```
src/agent_loop/
├── cli.py          # Click CLI commands
├── loop.py         # Main loop logic (LoopRunner)
├── preset.py       # Preset loading (Mode, Preset, ReviewConfig dataclasses)
├── review.py       # Review cycle logic (prompt building, review agent)
├── runner.py       # opencode subprocess wrapper
├── git.py          # Git operations (commit, squash)
└── presets/        # Built-in preset YAML files
```

## Key Files

- `cli.py` - Entry point, command definitions
- `loop.py` - Main iteration loop, mode cycling, review triggering, squash logic
- `preset.py` - YAML parsing, Mode/Preset/ReviewConfig dataclasses
- `review.py` - Review cycle prompt composition and execution
- `runner.py` - Subprocess wrapper for opencode CLI
- `git.py` - Commit and squash operations
- `presets/*.yaml` - Built-in presets for various code and documentation review tasks

## Development Notes

When making changes:
- Test the full loop flow: preset loading → iteration → review → squash
- Verify mode cycling wraps correctly (last mode → first mode → review)
- Review cycles run after completing all modes, not after each iteration
- Agents commit their own changes via prompts (no framework auto-commit)
- Ensure squash only squashes iteration commits, not unrelated changes

## Writing Prompts

For work on prompt-related tasks, see [docs/prompt_philosophy.md](docs/prompt_philosophy.md).
