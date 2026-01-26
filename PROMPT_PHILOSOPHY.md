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

### The 3-Step Pattern

Every mode should end with explicit verification:

```
**After completing your changes**, orchestrate verification:

1. Spawn a sub-agent to review your work. Give it:
   - [Specific task description]
   - The files you modified
   - [Specific things to check]

2. Spawn a filter sub-agent. Give it the verification feedback and ask:
   which concerns are genuine issues vs [category of false positives]?

3. Address filtered feedback, then commit.
```

This must be written out fully each time. The agent doesn't remember that other prompts had similar verification steps.

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
- [ ] **Verification included**: Full 3-step verification written out explicitly?
- [ ] **Inaction validated**: Does it say "no changes needed is valid"?
- [ ] **Deletion permitted**: Does it frame removal as valuable, not just allowed?
- [ ] **No expansion triggers**: No "comprehensive," "exhaustive," "thorough"?
