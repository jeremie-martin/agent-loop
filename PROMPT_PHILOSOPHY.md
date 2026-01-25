# Prompt Philosophy

Principles for writing effective agent prompts in iterative loops.

---

## Trusting Agent Judgment

Smart agents respond better to understanding what "good" looks like than to being told what to do.

### Describe outcomes, not steps

Say "concepts appear once" instead of "remove duplicates." The agent deduces which duplicates to remove and how to consolidate, producing better judgments.

### Prefer holistic prompts

Few well-scoped prompts work better than many narrow prompts that micromanage.

**Narrow** (avoid): separate modes for accuracy, structure, clarity
**Holistic** (prefer): improve quality, then ensure coherence

Holistic prompts reveal the full picture and enable richer trade-offs.

### Frame quality positively

"Keep it short" feels restrictive. "Every section earns its place" treats tightness as quality. The agent aims for quality, not rules.

Phrases like "reads as a coherent whole" put agents in an editor's mindset—shaping rather than adding.

### Guard against over-correction

Phrases like "genuinely improve" and "don't reorganize for the sake of reorganizing" prevent zealotry.

---

## Preventing Explosion

Documentation tends to grow. Each improvement adds a sentence, a section, a file. Without counter-pressure, docs become bloated.

### Deletion is value

Removing redundant content is as valuable as adding. Agents default to adding unless you explicitly permit deletion:

- "Consolidate near-duplicates"
- "Deleting a redundant test is as valuable as adding a missing one"
- "Fewer, better tests"

### Avoid expansion trigger words

"Comprehensive," "exhaustive," "thorough," "complete coverage"—these prime the agent toward more-is-better. Use "authoritative," "accurate," "coherent" instead.

### Use neutral action verbs

"Correcting, clarifying, consolidating, or restructuring"—all valid moves. No hierarchy where adding is default and removing requires justification.

### Embrace diminishing returns

Iterations naturally approach equilibrium—after several passes, there's less to do. This is success.

**Do** validate inaction: "If something already works well, leave it alone" and "'No changes needed' is a valid outcome."

**Don't** imply every iteration must produce changes. Agents should report "nothing to do" rather than invent work.

---

## Stateless Design

Each iteration starts fresh—no memory between iterations.

**Don't** assume state carries over: "Based on the previous step..." or "Continue where you left off..."
**Do** use existing artifacts: "Read the token definitions file," "Check git diff," "Find config in package.json."

Treat each prompt as a standalone task. Prompts should be complete without framework jargon like "preset," "cycle," "iteration." Include necessary context explicitly: task description, references to existing files, or git commands like `git status` and `git diff`.

If iterations need to pass information, write it to a file. Prefer discovering from existing artifacts.

### Ground claims in source

Require agents to verify claims against actual source code. Phrases like "before editing, read the corresponding source code" and "cite specific code locations" prevent factual drift.
