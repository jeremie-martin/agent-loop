# Prompt Philosophy

Principles for writing effective agent prompts in iterative loops.

*For an overview of agent-loop, see the [README](../README.md).*

## 1. Describe the destination, not the steps

Smart agents respond better to understanding what "good" looks like than to being told what to do. Instead of "remove duplicates," say "concepts appear once." The agent concludes on its own that duplicates should go, which produces better judgment about which duplicates and how to consolidate.

## 2. Frame conciseness as quality, not constraint

"Keep it short" feels like a restriction fighting against helpfulness. But "every section earns its place" treats tightness as a quality marker rather than a constraint. The agent aims for quality rather than following rules.

## 3. Reader-centered language

Phrases like "reads as a coherent whole" and "easy to follow" put the agent in an editor's mindset rather than a writer's. Writers add; editors shape. You want the shaping mindset.

## 4. Neutral action verbs

"Correcting, clarifying, consolidating, or restructuring"—all presented as equally valid moves. No implicit hierarchy where adding is the default and removing requires justification.

## 5. Avoid expansion trigger words

"Comprehensive," "exhaustive," "thorough," "complete coverage"—these prime the agent toward more-is-better. Use "authoritative," "accurate," "coherent" instead.

## 6. Guard against over-correction

Phrases like "genuinely improve" and "don't reorganize for the sake of reorganizing" prevent over-correction. You want judgment, not zealotry.

## 7. One purpose per prompt

Clean separation lets each pass do its job well. agent-loop cycles through separate modes, each with a single focus.

## 8. Agents are stateless—use artifacts

Each iteration starts with a fresh agent. There is no memory between iterations.

**Don't** write prompts that assume state carries over:
- "Based on the inventory from the previous step..." (what inventory?)
- "Continue where you left off..." (the agent has no context)
- "Build a picture of the codebase..." (the picture vanishes when the iteration ends)

**Do** write prompts that are self-contained:
- "Read the token definitions file, then..." (artifact exists in filesystem)
- "Check git diff to see what changed..." (artifact exists in git)
- "Find the configuration in package.json..." (artifact exists in filesystem)

If an iteration needs to pass information to the next, it must write that information to a file. But prefer designs where each iteration discovers what it needs from existing artifacts (source code, config files, git state).

## 9. Self-contained prompts

Agents don't know they're in a loop. Each prompt should be complete and task-focused without framework jargon like "preset," "cycle," or "iteration." The agent just sees a task to complete.

Context comes from:
- Task description (what the work is about)
- Existing files (source code, config, previous changes)
- Git state (uncommitted changes, recent commits)

## 10. Ground claims in source

For documentation work, require agents to verify claims against actual source code. Phrases like "before editing, read the corresponding source code" and "cite specific code locations" prevent factual drift over iterations.

## 11. Verify before moving on

For tasks with measurable correctness (CSS syntax, token references, build passes), instruct agents to verify each change before proceeding. "If you introduce errors, fix them before moving to the next file" prevents cascading breakage.

## 12. Filter feedback before acting

Review agents should filter their own feedback before acting. This two-step pattern (check → filter → act) prevents over-correction:

```yaml
review:
  check_prompt: |
    Verify that all token references are valid...
  filter_prompt: |
    Filter out:
    - Style opinions about naming
    - Suggestions to add new tokens (out of scope)
    Only act on actual breakages.
```

## 13. Scope reviews to relevant files

Review prompts should explicitly scope what files to examine:
- "Review only the documentation changes (markdown files, README, docs/)"
- "Review only the styling-related changes (CSS, SCSS, style files)"
- "Ignore any unrelated files that may appear in git diff"

This prevents the review agent from getting distracted by or incorrectly committing unrelated changes.

## 14. Embrace diminishing returns

Iterations naturally approach equilibrium. After several passes, most issues are fixed and there's less to do. This is success, not failure.

**Do** include language that validates inaction:
- "If something already works well, leave it alone"
- "If you find no meaningful gaps, make no changes"
- "'No changes needed' is a valid outcome"

**Don't** write prompts that imply every iteration must produce changes. Agents should feel comfortable reporting "nothing to do" rather than inventing work.

## 15. Bound sub-agent scope explicitly

When a mode spawns sub-agents for parallel work, each sub-agent operates without the parent's context. They need explicit bounds.

**Don't** write:
- "Launch sub-agents to handle each area. Each edits its area directly."

**Do** write:
- "Launch sub-agents. Give each the specific changes from git diff and instruction to update only what's directly affected—no broader improvements."

Sub-agents should receive: what changed, what they're allowed to touch, and explicit instruction to do minimal work.

## 16. Deletion is value

Removing something—a redundant test, a duplicate paragraph, a near-duplicate token—is as valuable as adding something. Make this explicit.

- "Consolidate near-duplicates"
- "Deleting a redundant test is as valuable as adding a missing one"
- "Fewer, better tests"

Without this framing, agents default to additive behavior. Explicit deletion language gives permission to subtract.

## Example in practice

The built-in `docs-review` preset demonstrates these principles with three modes (accuracy, structure, clarity) plus a review phase. Each mode has a single focus, uses destination-focused language, and is fully self-contained. The review phase catches factual drift by cross-checking against source code.

The `frontend-style` preset shows how to handle dependent work without relying on agent memory: centralization creates token files, adoption reads those files to discover available tokens, coherence reads them again to assess consistency. Each iteration discovers what it needs from artifacts, not from previous agent state.
