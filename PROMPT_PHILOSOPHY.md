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

## Outcome-Focused Prompts

Smart agents respond better to understanding what "good" looks like than to being told what to do. Describe the target state, not the steps to get there.

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

### Prefer Holistic Prompts

Few well-scoped prompts work better than many narrow prompts that micromanage. When multiple modes are appropriate, each should be a **different lens on the same goal**, not sequential steps of one process.

**Good** (independent lenses):
- Mode 1: "Improve documentation quality" (accuracy, clarity)
- Mode 2: "Ensure documentation coherence" (structure, redundancy)

Both modes are complete tasks. Either can run first. Neither depends on the other.

### When Specificity Helps

Some domains require technical details because agents may not know the patterns. Security vulnerabilities are a prime example—agents may not know that `shell=True` enables injection.

For these tasks, use a **hybrid approach**:

```yaml
# Holistic framing first
A secure codebase has no injection points. User input never flows
directly into dangerous operations without validation.

# Technical guidance as reference
Common patterns to address:
- SQL with string interpolation → parameterized queries
- Shell commands with user input → subprocess with array args
```

Frame technical details as "what good code does" rather than "steps to perform."

### Frame Quality Positively

"Keep it short" feels restrictive. "Every section earns its place" treats tightness as quality. Phrases like "genuinely improve" and "don't reorganize for the sake of reorganizing" prevent zealotry.

---

## Quality Over Quantity

Each invocation should leave the codebase better, not "completely fixed." Agents that try to do everything often do nothing well.

### Impact-Focused Language

| Instead of | Use |
|------------|-----|
| "Find all instances of..." | "Address the most impactful cases of..." |
| "Fix every X" | "Focus on changes that meaningfully improve..." |
| "Be thorough" | "Prioritize by impact" |
| "Comprehensive," "exhaustive" | "Meaningful," "effective" |

Phrases that prime for quality: "A few well-chosen fixes are better than many marginal ones," "Address clear wins first."

### The Progress Mindset

Good framing: "After your changes, the codebase should be measurably better at X."

This encourages impactful work without demanding perfection. An agent making three meaningful improvements is better than one attempting (and failing at) twenty.

### Natural Convergence

With quality-focused framing, each invocation picks the most valuable remaining work. Early passes fix obvious issues; later passes have less to do. This is healthy convergence, not failure.

---

## Preventing Explosion

Work tends to grow. Without counter-pressure, codebases become bloated.

### Deletion Is Value

Removing redundant content is as valuable as adding. Agents default to adding unless you explicitly permit deletion:

- "Consolidate near-duplicates"
- "Deleting a redundant test is as valuable as adding a missing one"
- "Fewer, better tests"

### Validate Inaction

"If something already works well, leave it alone" and "'No changes needed' is a valid outcome."

Don't imply every iteration must produce changes. Agents should report "nothing to do" rather than invent work.

---

## Documentation-Specific Guidance

Documentation tasks require additional constraints beyond code changes. Unlike code, documentation has no compiler, no tests, and no clear signal when it's "wrong." This makes explosion especially likely.

### The Maintenance Burden

Every line of documentation is a maintenance liability. Unlike code that fails visibly when behavior changes, documentation rots silently. Long docs become unread docs.

**Calibrate scope to maintenance capacity:**
- Internal-facing docs can assume context; external docs need more
- Frequently-changing features need minimal docs (they'll go stale)
- Stable APIs deserve thorough coverage

### Size Is a Quality Signal

For documentation, "comprehensive" is often an anti-pattern. A 50-line troubleshooting guide that covers common cases serves readers better than an 800-line guide that covers everything but nobody reads.

**Guidance for documentation prompts:**
- "Prioritize the 5 most common issues" over "document all known issues"
- "Keep sections scannable" (readers skim, they don't read)
- "A shorter doc that gets read beats a longer doc that doesn't"

### Deletion Is the Default

For code, deletion requires justification (is it really unused?). For documentation, **expansion** requires justification. The burden of proof should be inverted:

| Code | Documentation |
|------|---------------|
| "Can we safely delete this?" | "Does this earn its place?" |
| Add if functionality is missing | Add only if readers genuinely need it |
| Coverage is generally good | Coverage can be harmful (stale, overwhelming) |

**Frame deletion as the natural choice:**
- "Remove content that duplicates what code comments already say"
- "If readers can figure it out from the code, they don't need a doc"
- "Each section must justify its existence to readers"

### Audience-Appropriate Scope

Documentation has an audience that code doesn't. The same content might be essential for beginners and noise for experts.

**Require prompts to specify the audience:**
- "Internal team documentation" → assume familiarity, be terse
- "User-facing documentation" → define terms, include examples
- "Onboarding documentation" → explain why, not just what

Prompts that don't specify an audience tend to produce "comprehensive" docs that serve no one well.

### Measuring Success

Code quality has proxies: tests pass, linter is happy, type checker approves. Documentation has none of these. This makes it easy for an agent to "succeed" by adding volume.

**Explicit success criteria for doc tasks:**
- "Success is fewer total lines while covering the same topics"
- "Success is a reader being able to find X in under 30 seconds"
- "Success is removing content that doesn't match current behavior"

Never frame success as "more complete" or "more thorough"—these are traps.

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
- [ ] **Verification included**: Verification pattern written out explicitly?
- [ ] **Inaction validated**: Does it say "no changes needed is valid"?
- [ ] **Deletion permitted**: Does it frame removal as valuable, not just allowed?

**For documentation tasks:**
- [ ] **Audience specified**: Does it say who the documentation is for?
- [ ] **Size treated as cost**: Does it frame length as a liability, not a benefit?
- [ ] **Measurable success**: Is success defined without "comprehensive" or "thorough"?
- [ ] **Expansion requires justification**: Is adding content treated as needing a reason?
