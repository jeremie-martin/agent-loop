# Prompt Philosophy

Principles for writing effective agent prompts in iterative loops.

---

## Stateless Design (Most Important)

**Each agent invocation starts with zero memory.** There is no "previous mode," no "last iteration," no shared context. Every prompt must be self-contained.

### The Stateless Test

Before finalizing a prompt, ask: *"If this were the only prompt an agent ever saw, would it have everything needed to do the task?"*

If the answer is no, the prompt has a hidden dependency.

### Common Violations

**Cross-mode dependencies** (broken):
```yaml
modes:
  - name: survey
    prompt: "Find all naming inconsistencies and document them."
  - name: fix
    prompt: "Fix the inconsistencies identified in the survey phase."
```

The "fix" agent has no idea what the "survey" agent found. It starts fresh.

**Self-contained alternative** (works):
```yaml
modes:
  - name: consistency
    prompt: "Find naming inconsistencies and fix them."
```

Each invocation discovers AND acts. No handoff required.

### When Modes Can Depend on Each Other

Modes can have *implicit* dependencies through **artifacts in the codebase**—but only if those artifacts reliably exist.

**Works**: Mode 2 reads files that mode 1 created:
```yaml
- name: tokens
  prompt: "Create a design token file with color and spacing definitions."
- name: adoption
  prompt: "Read the design token file. Replace hardcoded values with token references."
```

Mode 2 reads actual files from disk, not mode 1's "memory."

**Broken**: Mode 2 reads git diff expecting to see mode 1's changes:
```yaml
- name: refactor
  prompt: "Refactor error handling. Commit your changes."
- name: propagation
  prompt: "Check git diff to see what changed. Update callers."
```

Mode 1 *committed*, so `git diff` shows nothing. Mode 2 sees an empty diff.

### Artifacts Must Actually Exist

If a prompt says "read X," X must exist when the agent runs. Consider:

- **Git diff**: Shows uncommitted changes only. If previous mode committed, diff is empty.
- **Git log**: Shows commits, but which ones? The agent doesn't know which are "recent."
- **Files**: Reliable if created by a previous mode, but fragile if the file path isn't predictable.

**Prefer self-contained modes** that discover from the codebase's current state rather than inferring what changed.

### No Framework Jargon

Agents don't know they're in a loop. These phrases are meaningless to them:

- ❌ "in this cycle"
- ❌ "from the previous iteration"
- ❌ "as identified in the survey mode"
- ❌ "continue where the last agent left off"

Write prompts as standalone tasks.

---

## Self-Contained Verification

Each prompt should include its own verification steps. Don't say "apply the same verification as before"—there is no "before."

### Sub-agents Need Context

Sub-agents start fresh—they haven't read the documentation the main agent read. The prompt_prefix instructs the main agent to:

1. Give sub-agents the exact file paths to relevant documentation
2. Explicitly instruct them to read those files completely before starting
3. Include any other specific files they need to examine

Do not just tell sub-agents to "read the documentation"—they often won't. Give them the paths directly.

**Future exploration**: An alternative approach is having the main agent summarize relevant conventions and pass them directly. This could be more efficient but risks missing important details. Worth experimenting with.

### Verification Patterns

**3-step pattern** (for subjective/design tasks where over-engineering is a risk):

```
1. Spawn a review sub-agent with: file paths to docs, files modified, what to check
2. Spawn a filter sub-agent to separate genuine issues from over-caution
3. Address filtered feedback, then commit
```

Use for: security hardening, dependency injection, interface design, API contracts, type boundaries, config externalization, error handling patterns.

**2-step pattern** (for factual/deterministic tasks):

```
Spawn a review sub-agent with: file paths to docs, files modified, what to check
Address the feedback, then commit
```

Use for: documentation review, dead code removal, propagation/sync tasks, token adoption, log message quality, test consolidation.

The filter step prevents over-defensive feedback from causing unnecessary changes. Skip it when the verification is more factual ("does this match?" vs "is this good design?").

---

## Trusting Agent Judgment

Smart agents respond better to understanding what "good" looks like than to being told what to do.

### Describe Outcomes, Not Steps

Say "concepts appear once" instead of "remove duplicates." The agent deduces which duplicates to remove and how to consolidate, producing better judgments.

### Prefer Holistic Prompts

Few well-scoped prompts work better than many narrow prompts that micromanage.

- **Narrow** (avoid): separate modes for accuracy, structure, clarity
- **Holistic** (prefer): one mode for quality that addresses all three

Holistic prompts reveal the full picture and enable richer trade-offs.

### Multi-Mode Design

When multiple modes are appropriate, each should be a **different lens on the same goal**, not sequential steps of one process.

**Good** (independent lenses):
- Mode 1: "Improve documentation quality" (accuracy, clarity)
- Mode 2: "Ensure documentation coherence" (structure, redundancy)

Both modes are complete tasks. Either can run first. Neither depends on the other.

**Bad** (sequential steps):
- Mode 1: "Identify documentation problems"
- Mode 2: "Fix the identified problems"

Mode 2 is useless without mode 1's output.

### Frame Quality Positively

"Keep it short" feels restrictive. "Every section earns its place" treats tightness as quality. The agent aims for quality, not rules.

Phrases like "reads as a coherent whole" put agents in an editor's mindset—shaping rather than adding.

### Guard Against Over-Correction

Phrases like "genuinely improve" and "don't reorganize for the sake of reorganizing" prevent zealotry.

---

## Target State Clarity

Describe what "done" looks like rather than the steps to get there. Agents are intelligent—they can figure out *how* once they understand *what*.

### Paint the Picture

**Procedural** (avoid):
```
1. Survey the codebase
2. Find all instances of X
3. For each instance, check Y
4. Apply fix Z
```

**Target-state** (prefer):
```
In a well-maintained codebase, X never appears unguarded. Every instance
either uses Y or has documented justification.
```

The agent deduces the survey, the search, and the fixes. You've told it what good looks like.

### State the Goal, Not the Audit

Instead of "Find A, B, and C patterns and fix them," try "A codebase free of pattern X means..."—then describe what that looks like. The checklist can follow as guidance, but the framing puts focus on the outcome.

### Exception: Technical Specificity

Some domains require specificity because the agent may not know the technical patterns. Security vulnerabilities are a prime example:

- Agents may not know that `shell=True` enables injection
- Agents may not recognize parameterized query syntax
- Specific attack patterns need explicit mention

In these cases, include technical details—but frame them as "what good code does" rather than "steps to perform."

---

## Implicit Impact Framing

The language you use shapes how agents approach work. Certain phrases encourage meaningful, high-value changes without mentioning iteration.

### Language That Encourages Impact

| Instead of | Use |
|------------|-----|
| "Find all instances of..." | "Address the most impactful cases of..." |
| "Fix every X" | "Focus on changes that meaningfully improve..." |
| "Be thorough" | "Prioritize by impact" |
| "Check everything" | "Focus on what matters most" |

### Quality Signals

Phrases that prime for quality over quantity:

- "Prioritize changes that readers will notice"
- "Focus on the improvements that matter"
- "A few well-chosen fixes are better than many marginal ones"
- "Address clear wins first"

These naturally encourage the agent to make meaningful progress without trying to do everything.

### Avoid Exhaustiveness Framing

"Comprehensive," "complete," and "exhaustive" prime agents toward quantity. The agent tries to find *everything* rather than making *progress*. Use "effective," "meaningful," or "impactful" instead.

**Anti-pattern**:
```yaml
prompt: "Find and fix ALL naming inconsistencies. Be thorough and comprehensive."
# Result: Agent attempts 50 marginal renames, breaks things, or times out.
```

**Better**:
```yaml
prompt: "Focus on naming inconsistencies that hurt readability. A few clear fixes are better than many marginal ones."
# Result: Agent makes meaningful progress that accumulates across invocations.
```

---

## Quality Over Quantity

Each invocation should leave the codebase better, not "completely fixed." Agents that try to do everything often do nothing well.

### Encourage Meaningful Progress

Prompts that work well across multiple invocations:

- "Make the changes that most improve X" (not "fix all X problems")
- "Address clear violations" (not "ensure complete compliance")
- "Focus on what will make the biggest difference" (not "be thorough")

### The Progress Mindset

Good framing: "After your changes, the codebase should be measurably better at X."

This encourages impactful work without demanding perfection. An agent making three meaningful improvements is better than one attempting (and failing at) twenty.

### Natural Convergence

With quality-focused framing, each invocation picks the most valuable remaining work. Early passes fix obvious issues; later passes have less to do. This is healthy convergence, not failure.

---

## When Specificity Helps vs Hurts

Not all prompts benefit from the same level of detail. Match specificity to the task.

### Tasks That Benefit from Holistic Framing

- **Naming consistency**: The agent can survey and decide what's "dominant"
- **Documentation quality**: The agent knows good writing when it sees it
- **Code style**: The agent understands readability
- **Dead code removal**: The agent can trace references

For these, describe the target state and let the agent judge.

### Tasks That Need Specificity

- **Security hardening**: Specific vulnerability patterns must be named
- **API consistency**: Specific conventions must be stated if non-obvious
- **Framework patterns**: The agent may not know framework-specific best practices

For these, provide technical details—but frame them as "what good looks like" not "steps to follow."

### The Hybrid Approach

Many tasks benefit from both:
1. **Framing**: A holistic target-state description
2. **Guidance**: Specific patterns or examples as reference

```yaml
# Holistic framing first
A secure codebase has no injection points. User input never flows
directly into dangerous operations without validation.

# Technical guidance as reference
Common patterns to address:
- SQL with string interpolation → parameterized queries
- Shell commands with user input → subprocess with array args
- File paths from user input → validate and resolve first
```

---

## Preventing Explosion

Work tends to grow. Each improvement adds a sentence, a function, a file. Without counter-pressure, codebases become bloated.

### Deletion Is Value

Removing redundant content is as valuable as adding. Agents default to adding unless you explicitly permit deletion:

- "Consolidate near-duplicates"
- "Deleting a redundant test is as valuable as adding a missing one"
- "Fewer, better tests"

### Avoid Expansion Trigger Words

"Comprehensive," "exhaustive," "thorough," "complete coverage"—these prime the agent toward more-is-better. Use "authoritative," "accurate," "coherent" instead.

### Use Neutral Action Verbs

"Correcting, clarifying, consolidating, or restructuring"—all valid moves. No hierarchy where adding is default and removing requires justification.

### Embrace Diminishing Returns

Iterations naturally approach equilibrium—after several passes, there's less to do. This is success.

**Do** validate inaction: "If something already works well, leave it alone" and "'No changes needed' is a valid outcome."

**Don't** imply every iteration must produce changes. Agents should report "nothing to do" rather than invent work.

---

## Ground Claims in Source

Require agents to verify claims against actual source code. Phrases like "before editing, read the corresponding source code" and "cite specific code locations" prevent factual drift.

---

## Quick Reference: Prompt Checklist

Before finalizing a prompt, verify:

- [ ] **Stateless**: Would this work if it were the agent's first and only task?
- [ ] **Self-contained**: Does it discover AND act, or does it depend on another mode's output?
- [ ] **No jargon**: No "cycle," "iteration," "previous mode," "as before"?
- [ ] **Target-state framed**: Does it describe what "done" looks like rather than steps?
- [ ] **Impact language**: Uses "meaningful," "clear wins" not "comprehensive," "thorough"?
- [ ] **Quality over quantity**: Encourages few impactful changes over many marginal ones?
- [ ] **Verification included**: Full 3-step verification written out explicitly?
- [ ] **Inaction validated**: Does it say "no changes needed is valid"?
- [ ] **Deletion permitted**: Does it frame removal as valuable, not just allowed?
