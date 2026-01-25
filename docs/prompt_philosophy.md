# Prompt Philosophy

Principles for writing effective agent prompts in iterative loops.

*For an overview of agent-loop, see the [README](../README.md).*

---

## Trusting Agent Judgment

### Describe outcomes, not steps

Smart agents respond better to understanding what "good" looks like than to being told what to do. Instead of "remove duplicates," say "concepts appear once." The agent concludes on its own that duplicates should go, which produces better judgment about which duplicates and how to consolidate.

### Holistic prompts over narrow modes

Prefer fewer prompts that handle larger, well-scoped tasks autonomously over many narrow prompts that micromanage implementation.

**Narrow** (avoid):
- Mode 1: Check accuracy
- Mode 2: Check structure
- Mode 3: Check clarity

**Holistic** (prefer):
- Mode 1: Improve quality (agent decides what needs attention)
- Mode 2: Ensure coherence (counter-balance to mode 1)

Benefits:
- Trusts agent judgment about what matters
- Allows agent to see the full picture, not just one dimension
- Reduces artificial separation between related concerns
- Enables richer trade-off decisions within a single pass
- Complementary modes balance each other (improve vs consolidate)

### Frame quality positively

"Keep it short" feels like a restriction fighting against helpfulness. But "every section earns its place" treats tightness as a quality marker. The agent aims for quality rather than following rules.

Phrases like "reads as a coherent whole" and "easy to follow" put the agent in an editor's mindset rather than a writer's. Writers add; editors shape. You want the shaping mindset.

### Guard against over-correction

Phrases like "genuinely improve" and "don't reorganize for the sake of reorganizing" prevent over-correction. You want judgment, not zealotry.

---

## Preventing Explosion

### Deletion is value

Removing something—a redundant test, a duplicate paragraph, a near-duplicate token—is as valuable as adding something. Make this explicit:

- "Consolidate near-duplicates"
- "Deleting a redundant test is as valuable as adding a missing one"
- "Fewer, better tests"

Without this framing, agents default to additive behavior. Explicit deletion language gives permission to subtract.

### Avoid expansion trigger words

"Comprehensive," "exhaustive," "thorough," "complete coverage"—these prime the agent toward more-is-better. Use "authoritative," "accurate," "coherent" instead.

### Use neutral action verbs

"Correcting, clarifying, consolidating, or restructuring"—all presented as equally valid moves. No implicit hierarchy where adding is the default and removing requires justification.

### Embrace diminishing returns

Iterations naturally approach equilibrium. After several passes, most issues are fixed and there's less to do. This is success, not failure.

**Do** include language that validates inaction:
- "If something already works well, leave it alone"
- "If you find no meaningful gaps, make no changes"
- "'No changes needed' is a valid outcome"

**Don't** write prompts that imply every iteration must produce changes. Agents should feel comfortable reporting "nothing to do" rather than inventing work.

---

## Stateless Design

### Agents are stateless—use artifacts

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

### Self-contained prompts

Agents don't know they're in a loop. Each prompt should be complete and task-focused without framework jargon like "preset," "cycle," or "iteration." The agent just sees a task to complete.

Context comes from:
- Task description (what the work is about)
- Existing files (source code, config, previous changes)
- Git state (uncommitted changes, recent commits)

### Ground claims in source

For documentation work, require agents to verify claims against actual source code. Phrases like "before editing, read the corresponding source code" and "cite specific code locations" prevent factual drift over iterations.

---

## Self-Verification

### Embed verify-filter-act in prompts

For holistic tasks, embed the verification pattern directly into the prompt:

1. **Verify**: Spawn a sub-agent with task context and your changes. Ask it to identify missed requirements, potential issues, edge cases, and simplification opportunities.

2. **Filter**: Spawn another sub-agent with the verification feedback. Ask it to identify which feedback is genuinely applicable vs over-defensive, speculative, or based on misunderstanding.

3. **Act**: Address only the filtered feedback. Make changes where warranted, preserve the original scope. Commit only after this step.

This works better than external review cycles because:
- The agent who made changes orchestrates verification with full context
- Verification happens while context is fresh
- The filter step prevents over-correction without a separate mode
- Sub-agents don't commit—only the final act step commits

### Verify before moving on

For tasks with measurable correctness (CSS syntax, token references, build passes), instruct agents to verify each change before proceeding. "If you introduce errors, fix them before moving to the next file" prevents cascading breakage.

### Bound sub-agent scope explicitly

When a mode spawns sub-agents for parallel work, each sub-agent operates without the parent's context. They need explicit bounds.

**Don't** write:
- "Launch sub-agents to handle each area. Each edits its area directly."

**Do** write:
- "Launch sub-agents. Give each the specific changes from git diff and instruction to update only what's directly affected—no broader improvements."

Sub-agents should receive: what changed, what they're allowed to touch, and explicit instruction to do minimal work.

---

## Test Handling

### Trust asymmetry for failing tests

When a test fails, there are two possibilities: the test is wrong, or the implementation is wrong. Agents are biased toward making things pass, which can mask real bugs.

**Asymmetric trust rules:**
- Tests that *existed before* this iteration are trusted. If they fail after your changes, you broke something—fix your changes, not the test.
- Tests you *just wrote* are suspect. If they fail, investigate: fix your test if it's wrong, but if you found a real bug, don't delete or weaken the test.

**For new tests that reveal bugs:**
- Don't delete the test (loses bug detection)
- Don't change assertions to match broken behavior (masks the bug)
- Mark as skipped with a clear reason: `@pytest.mark.skip(reason="Reveals bug: ...")`
- This preserves the test as documentation while not breaking CI

The principle: never make a test pass by changing what it expects. Make it pass by fixing what's broken.

---

## Example in Practice

The built-in `docs-review` preset demonstrates these principles with two complementary modes: quality (holistic improvement) and coherence (anti-explosion). Each mode trusts the agent to identify what needs attention rather than prescribing narrow checks. The self-review pattern is embedded directly—verify changes with a sub-agent, filter feedback with another, then act on what's genuinely applicable.

The `frontend-style` preset shows how to handle dependent work without relying on agent memory: tokens mode creates central definitions, adoption mode reads those definitions to discover available tokens. Each iteration discovers what it needs from artifacts, not from previous agent state. Both modes include self-orchestrated verification before committing.
