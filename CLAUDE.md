# CLAUDE.md

Guidance for Claude Code when working with this repository.

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

## Development Notes

When making changes:
- Test the full loop flow: preset loading → iteration → review → squash
- Verify mode cycling wraps correctly (last mode → first mode → review)
- Review cycles (if enabled in preset) run after completing all modes in a cycle
- Agents commit their own changes via prompts (no framework auto-commit)
- Ensure squash only squashes iteration commits, not unrelated changes

### Test Handling

When working with failing tests:

**Asymmetric trust:**
- Tests that existed before this iteration are trusted. If they fail after your changes, fix your changes, not the test.
- Tests you just wrote are suspect. If they fail, investigate: fix the test if wrong, but don't delete or weaken tests that reveal real bugs.

**For new tests that reveal bugs:**
- Mark as skipped: `@pytest.mark.skip(reason="Reveals bug: ...")`
- Preserves documentation without breaking CI
- Never make a test pass by changing what it expects—fix what's broken instead
