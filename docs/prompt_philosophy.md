# Prompt Philosophy

Principles for writing effective agent prompts in iterative loops.

## 1. Describe the destination, not the steps

Smart agents respond better to understanding what "good" looks like than to being told what to do. Instead of "remove duplicates," say "concepts appear once." The agent concludes *on its own* that duplicates should go—which produces better judgment about *which* duplicates and *how* to consolidate.

## 2. Frame conciseness as quality, not constraint

"Keep it short" feels like a restriction fighting against helpfulness. But "every section earns its place" frames tightness as what good work *naturally has*. The agent aims for quality rather than following a rule.

## 3. Reader-centered language

Phrases like "reads as a coherent whole" and "easy to follow" put the agent in an editor's mindset rather than a writer's. Writers add; editors shape. You want the shaping mindset.

## 4. Neutral action verbs

"Correcting, clarifying, consolidating, or restructuring"—all presented as equally valid moves. No implicit hierarchy that says adding is the default and removing requires justification.

## 5. Avoid expansion trigger words

"Comprehensive," "exhaustive," "thorough," "complete coverage"—these prime the agent toward more-is-better. Use "authoritative," "accurate," "coherent" instead.

## 6. Guard against over-correction

"Genuinely improve" and "don't reorganize for the sake of reorganizing" prevent the agent from swinging too far. You want judgment, not zealotry.

## 7. One purpose per prompt

Mixing concerns creates conflicts. Clean separation lets each pass do its job well. This is why agent-loop uses separate modes that cycle through—each mode has a single focus.
